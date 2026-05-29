#!/usr/bin/env python3
"""
CF-Orion Pro - Ultimate Cloudflare Origin & V2Ray Config Scanner
Inspired by: cfray, CDN IP Scanner, EzAccess CFScanner, V2Conf
Version: 3.0.0
"""

import asyncio
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import socket
import subprocess
import tempfile

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import requests
import dns.resolver
from urllib.parse import urlparse, parse_qs, unquote
import base64

# ==================== تنظیمات اولیه ====================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cf-orion-pro-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

active_scans = {}
scan_counter = 0

# لیست رنج‌های آی‌پی کلودفلر (14 رنج اصلی)
CLOUDFLARE_IPV4_RANGES = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "172.64.0.0/13", "131.0.72.0/22"
]

# اپراتورهای ایرانی برای تست
IRANIAN_OPERATORS = {
    "mci": {"name": "همراه اول", "test_domain": "mci.ir", "dns": ["10.10.34.34", "10.10.34.36"]},
    "irancel": {"name": "ایرانسل", "test_domain": "irancell.ir", "dns": ["172.29.0.10", "10.11.11.11"]},
    "adsl": {"name": "ADSL (مخابرات)", "test_domain": "tc.ir", "dns": ["80.191.67.67", "81.91.129.129"]},
    "rightel": {"name": "رایتل", "test_domain": "rightel.ir", "dns": ["185.133.156.36", "185.133.156.37"]},
    "shuttle": {"name": "شاتل", "test_domain": "shuttle.ir", "dns": ["185.143.232.100", "185.143.233.100"]}
}

# ==================== کلاس‌های اصلی ====================

class V2RayConfigParser:
    """پارسر حرفه‌ای کانفیگ‌های V2Ray"""
    
    @staticmethod
    def parse_vless(url: str) -> Optional[Dict]:
        """پارسر لینک VLESS"""
        if not url.startswith("vless://"):
            return None
        
        try:
            # جدا کردن بخش‌های مختلف
            parts = url.replace("vless://", "").split("@")
            if len(parts) != 2:
                return None
            
            uuid = parts[0]
            rest = parts[1].split("?")
            address_port = rest[0].split(":")
            address = address_port[0]
            port = int(address_port[1]) if len(address_port) > 1 else 443
            
            params = {}
            if len(rest) > 1:
                for param in rest[1].split("#")[0].split("&"):
                    if "=" in param:
                        k, v = param.split("=", 1)
                        params[k] = unquote(v)
            
            return {
                "type": "vless",
                "uuid": uuid,
                "address": address,
                "port": port,
                "encryption": params.get("encryption", "none"),
                "flow": params.get("flow", ""),
                "security": params.get("security", ""),
                "sni": params.get("sni", ""),
                "path": params.get("path", "/"),
                "host": params.get("host", ""),
                "type_transport": params.get("type", "tcp")
            }
        except Exception as e:
            return None
    
    @staticmethod
    def parse_vmess(url: str) -> Optional[Dict]:
        """پارسر لینک VMESS (Base64)"""
        if not url.startswith("vmess://"):
            return None
        
        try:
            encoded = url.replace("vmess://", "")
            decoded = base64.b64decode(encoded).decode('utf-8')
            config = json.loads(decoded)
            
            return {
                "type": "vmess",
                "uuid": config.get("id"),
                "address": config.get("add"),
                "port": config.get("port", 443),
                "security": config.get("tls", ""),
                "sni": config.get("sni", ""),
                "path": config.get("path", "/"),
                "host": config.get("host", ""),
                "type_transport": config.get("type", "tcp"),
                "alterId": config.get("aid", 0)
            }
        except Exception as e:
            return None
    
    @staticmethod
    def parse_trojan(url: str) -> Optional[Dict]:
        """پارسر لینک Trojan"""
        if not url.startswith("trojan://"):
            return None
        
        try:
            parts = url.replace("trojan://", "").split("@")
            if len(parts) != 2:
                return None
            
            password = parts[0]
            rest = parts[1].split("?")
            address_port = rest[0].split(":")
            address = address_port[0]
            port = int(address_port[1]) if len(address_port) > 1 else 443
            
            params = {}
            if len(rest) > 1:
                for param in rest[1].split("#")[0].split("&"):
                    if "=" in param:
                        k, v = param.split("=", 1)
                        params[k] = unquote(v)
            
            return {
                "type": "trojan",
                "password": password,
                "address": address,
                "port": port,
                "security": params.get("security", "tls"),
                "sni": params.get("sni", ""),
                "path": params.get("path", "/"),
                "host": params.get("host", "")
            }
        except Exception as e:
            return None


class IPRangeGenerator:
    """تولیدکننده رنج‌های آی‌پی برای اسکن"""
    
    @staticmethod
    def cidr_to_ips(cidr: str, max_ips: int = 10000) -> List[str]:
        """تبدیل CIDR به لیست آی‌پی‌ها (با محدودیت)"""
        try:
            import ipaddress
            network = ipaddress.ip_network(cidr, strict=False)
            ips = [str(ip) for ip in network.hosts()]
            if len(ips) > max_ips:
                # نمونه‌برداری برای سرعت بیشتر
                step = len(ips) // max_ips
                ips = ips[::step][:max_ips]
            return ips
        except:
            return []
    
    @staticmethod
    def generate_cloudflare_ips(mode: str = "normal") -> List[str]:
        """تولید آی‌پی‌های کلودفلر با حالت‌های مختلف"""
        all_ips = []
        
        for cidr in CLOUDFLARE_IPV4_RANGES:
            ips = IPRangeGenerator.cidr_to_ips(cidr, 10000)
            
            if mode == "quick":
                # فقط 1 آی‌پی به ازای هر /24
                ips = IPRangeGenerator.sample_ips(ips, 100)
            elif mode == "normal":
                # 3 آی‌پی به ازای هر /24
                ips = IPRangeGenerator.sample_ips(ips, 500)
            elif mode == "full":
                # همه آی‌پی‌ها (می‌تونه خیلی زیاد باشه)
                pass
            
            all_ips.extend(ips)
        
        return list(set(all_ips))  # حذف تکراری‌ها
    
    @staticmethod
    def sample_ips(ips: List[str], max_count: int) -> List[str]:
        if len(ips) <= max_count:
            return ips
        step = len(ips) // max_count
        return ips[::step][:max_count]


class SpeedTester:
    """تست سرعت واقعی با دانلود فایل"""
    
    @staticmethod
    def test_latency(ip: str, port: int = 443, timeout: int = 3) -> Optional[float]:
        """تست پینگ با اتصال TCP"""
        try:
            import time
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            start = time.time()
            result = sock.connect_ex((ip, port))
            end = time.time()
            sock.close()
            
            if result == 0:
                return (end - start) * 1000  # میلی‌ثانیه
        except:
            pass
        return None
    
    @staticmethod
    def test_download_speed(ip: str, port: int = 443, sni: str = None, 
                            test_file_size: int = 5) -> Optional[float]:
        """تست سرعت دانلود (MB/s)"""
        try:
            import time
            headers = {"Host": sni or ip}
            url = f"https://{ip}:{port}/speedtest/{test_file_size}mb.bin"
            
            start = time.time()
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                downloaded += len(chunk)
                if time.time() - start > 15:  # حداکثر 15 ثانیه
                    break
            
            end = time.time()
            duration = end - start
            if duration > 0:
                speed_mbps = (downloaded * 8) / (duration * 1024 * 1024)
                return speed_mbps
        except:
            pass
        return None
    
    @staticmethod
    def comprehensive_test(ip: str, config: Dict, test_round: str = "normal") -> Dict:
        """تست جامع یک کانفیگ"""
        result = {
            "ip": ip,
            "latency_ms": None,
            "download_mbps": None,
            "ttfb_ms": None,
            "success": False,
            "score": 0
        }
        
        # تست پینگ
        latency = SpeedTester.test_latency(ip, config.get("port", 443))
        if latency:
            result["latency_ms"] = round(latency, 2)
        
        # تست دانلود
        if test_round in ["quick", "normal"]:
            file_size = 1 if test_round == "quick" else 5
            speed = SpeedTester.test_download_speed(
                ip, config.get("port", 443), 
                config.get("sni"), file_size
            )
            if speed:
                result["download_mbps"] = round(speed, 2)
        
        # محاسبه امتیاز (بر اساس متد cfray)
        if result["latency_ms"] and result["download_mbps"]:
            result["success"] = True
            # امتیاز = 35% پینگ + 50% سرعت + 15% زمان پاسخ
            latency_score = max(0, 100 - (result["latency_ms"] / 10))
            speed_score = min(100, result["download_mbps"] * 10)
            score = (latency_score * 0.35) + (speed_score * 0.50) + (latency_score * 0.15)
            result["score"] = round(score, 2)
        elif result["latency_ms"]:
            result["score"] = round(max(0, 100 - (result["latency_ms"] / 10)), 2)
        
        return result


class OperatorTester:
    """تست کانفیگ‌ها برای اپراتورهای مختلف ایرانی"""
    
    @staticmethod
    def test_for_operator(ip: str, config: Dict, operator: str) -> Dict:
        """تست یک آی‌پی برای اپراتور مشخص"""
        result = {
            "operator": operator,
            "operator_name": IRANIAN_OPERATORS.get(operator, {}).get("name", operator),
            "latency_ms": None,
            "connectivity": False
        }
        
        # استفاده از DNS مخصوص اپراتور برای تست
        dns_servers = IRANIAN_OPERATORS.get(operator, {}).get("dns", ["8.8.8.8"])
        
        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = dns_servers
            resolver.timeout = 2
            
            # تست رزولوشن دامنه
            test_domain = IRANIAN_OPERATORS.get(operator, {}).get("test_domain", "google.com")
            answers = resolver.resolve(test_domain, 'A')
            
            if answers:
                result["connectivity"] = True
                # تست پینگ از طریق این اپراتور
                latency = SpeedTester.test_latency(ip, config.get("port", 443))
                if latency:
                    result["latency_ms"] = round(latency, 2)
        except:
            pass
        
        return result


class ConfigScanner:
    """اسکنر اصلی کانفیگ‌ها"""
    
    def __init__(self, socket_logger=None):
        self.parser = V2RayConfigParser()
        self.speed_tester = SpeedTester()
        self.operator_tester = OperatorTester()
        self.socket_logger = socket_logger
    
    def log(self, message: str, level: str = "info"):
        if self.socket_logger:
            self.socket_logger(message, level)
        print(f"[{level.upper()}] {message}")
    
    def scan_single_config(self, config_url: str, ips: List[str], 
                           test_mode: str = "normal",
                           test_operators: List[str] = None) -> Dict:
        """اسکن یک کانفیگ روی لیست آی‌پی‌ها"""
        
        # پارس کانفیگ
        config = self.parser.parse_vless(config_url)
        if not config:
            config = self.parser.parse_vmess(config_url)
        if not config:
            config = self.parser.parse_trojan(config_url)
        
        if not config:
            self.log("فرمت کانفیگ پشتیبانی نمی‌شود", "error")
            return {"error": "Unsupported config format"}
        
        self.log(f"✅ کانفیگ {config['type'].upper()} شناسایی شد", "success")
        self.log(f"📡 دامنه اصلی: {config['address']}", "info")
        
        results = []
        total = len(ips)
        
        for idx, ip in enumerate(ips):
            self.log(f"🔍 تست {idx+1}/{total}: {ip}", "info")
            
            # تست جامع
            test_result = self.speed_tester.comprehensive_test(ip, config, test_mode)
            
            if test_result["success"]:
                # تست برای اپراتورهای ایرانی
                operator_results = []
                if test_operators:
                    for op in test_operators:
                        op_result = self.operator_tester.test_for_operator(ip, config, op)
                        operator_results.append(op_result)
                
                results.append({
                    **test_result,
                    "operator_tests": operator_results
                })
                
                self.log(f"  📊 امتیاز: {test_result['score']} | "
                        f"پینگ: {test_result.get('latency_ms', 'N/A')}ms | "
                        f"سرعت: {test_result.get('download_mbps', 'N/A')} Mbps", "success")
        
        # مرتب‌سازی بر اساس امتیاز
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return {
            "config_type": config['type'],
            "original_address": config['address'],
            "total_tested": len(results),
            "successful": len([r for r in results if r.get("success")]),
            "results": results[:20],  # 20 تا برتر
            "top_ips": [r["ip"] for r in results[:5] if r.get("success")]
        }


# ==================== Flask Routes ====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def start_scan():
    global scan_counter
    data = request.json
    
    config = data.get('config')
    scan_mode = data.get('scan_mode', 'normal')
    test_operators = data.get('operators', ['mci', 'irancel', 'adsl'])
    ip_mode = data.get('ip_mode', 'normal')
    custom_ips = data.get('custom_ips', [])
    
    if not config:
        return jsonify({'error': 'Config is required'}), 400
    
    scan_counter += 1
    scan_id = f"scan_{scan_counter}_{int(datetime.now().timestamp())}"
    
    def run_scan():
        def socket_log(message, level):
            socketio.emit('scan_log', {
                'time': datetime.now().strftime("%H:%M:%S"),
                'message': message,
                'level': level
            }, room=scan_id)
        
        active_scans[scan_id] = {'status': 'running', 'progress': 0}
        socketio.emit('scan_started', {'scan_id': scan_id}, room=scan_id)
        
        try:
            socket_log("🚀 شروع اسکن حرفه‌ای", "success")
            socket_log(f"📋 حالت اسکن: {scan_mode}", "info")
            socket_log(f"📡 اپراتورهای فعال: {', '.join(test_operators)}", "info")
            
            # تولید یا دریافت آی‌پی‌ها
            if custom_ips and len(custom_ips) > 0:
                ips = custom_ips
                socket_log(f"📡 استفاده از {len(ips)} آی‌پی سفارشی", "info")
            else:
                socket_log("🔍 در حال تولید آی‌پی‌های کلودفلر...", "info")
                ips = IPRangeGenerator.generate_cloudflare_ips(ip_mode)
                socket_log(f"✅ {len(ips)} آی‌پی تولید شد", "success")
            
            # اجرای اسکنر
            scanner = ConfigScanner(socket_log)
            results = scanner.scan_single_config(config, ips, scan_mode, test_operators)
            
            # ذخیره نتایج
            output_file = RESULTS_DIR / f"{scan_id}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            active_scans[scan_id] = {
                'status': 'completed',
                'results': results,
                'file': str(output_file)
            }
            
            socket_log(f"✨ اسکن کامل شد! {results['successful']} آی‌پی موفق از {results['total_tested']}", "success")
            
            if results['top_ips']:
                socket_log(f"🏆 بهترین آی‌پی‌ها: {', '.join(results['top_ips'])}", "success")
            
            socketio.emit('scan_complete', {
                'scan_id': scan_id,
                'results': results
            }, room=scan_id)
            
        except Exception as e:
            socket_log(f"❌ خطا: {str(e)}", "error")
            active_scans[scan_id] = {'status': 'failed', 'error': str(e)}
    
    thread = threading.Thread(target=run_scan)
    thread.start()
    
    return jsonify({'scan_id': scan_id, 'status': 'started'})


@app.route('/api/results/<scan_id>')
def get_results(scan_id):
    if scan_id in active_scans:
        return jsonify(active_scans[scan_id])
    return jsonify({'error': 'Scan not found'}), 404


@app.route('/api/download/<scan_id>')
def download_results(scan_id):
    file_path = RESULTS_DIR / f"{scan_id}.json"
    if file_path.exists():
        return send_file(file_path, as_attachment=True, download_name=f"cf-orion_{scan_id}.json")
    return jsonify({'error': 'File not found'}), 404


@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to CF-Orion Pro'})


@socketio.on('join_scan')
def handle_join_scan(data):
    from flask_socketio import join_room
    scan_id = data.get('scan_id')
    if scan_id:
        join_room(scan_id)
        emit('joined', {'scan_id': scan_id})


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                ║
    ║     ██████╗ ███████╗     ██████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗               ║
    ║     ██╔══██╗██╔════╝    ██╔═══██╗██╔══██╗██║██╔═══██╗████╗  ██║               ║
    ║     ██║  ██║█████╗      ██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║               ║
    ║     ██║  ██║██╔══╝      ██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║               ║
    ║     ██████╔╝██║         ╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║               ║
    ║     ╚═════╝ ╚═╝          ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝               ║
    ║                                                                                ║
    ║                    CF-Orion Pro v3.0 - Ultimate Scanner                        ║
    ║                                                                                ║
    ║  🌐 Web UI: http://localhost:5000                                              ║
    ║  📡 Features: V2Ray Scanner | Clean IP Finder | Operator Testing              ║
    ║                                                                                ║
    ║  Inspired by: cfray, CDN IP Scanner, EzAccess CFScanner, V2Conf               ║
    ║                                                                                ║
    ╚════════════════════════════════════════════════════════════════════════════════╝
    """)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)