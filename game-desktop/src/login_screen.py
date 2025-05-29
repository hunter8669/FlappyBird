#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏内登录界面模块
提供登录、注册和用户信息显示功能
"""

import pygame
from pygame.locals import K_ESCAPE, K_BACKSPACE, K_RETURN, K_TAB, KEYDOWN
from .utils import get_font

class LoginScreen:
    def __init__(self, config, network_manager):
        self.config = config
        self.network = network_manager
        
        # 界面状态
        self.current_screen = "main"  # main, login, register, profile
        self.message = ""
        self.message_color = (255, 255, 255)
        
        # 输入框
        self.input_fields = {
            "username": "",
            "password": "",
            "email": "",
            "confirm_password": ""
        }
        self.active_field = "username"
        self.input_active = False
        
        # 字体
        try:
            self.title_font = get_font('SimHei', 32)
            self.button_font = get_font('SimHei', 20)
            self.input_font = get_font('SimHei', 18)
            self.message_font = get_font('SimHei', 16)
        except:
            # fallback fonts
            self.title_font = pygame.font.Font(None, 32)
            self.button_font = pygame.font.Font(None, 20)
            self.input_font = pygame.font.Font(None, 18)
            self.message_font = pygame.font.Font(None, 16)
        
        # 颜色定义
        self.colors = {
            "primary": (64, 128, 255),
            "primary_hover": (48, 96, 192),
            "secondary": (128, 128, 128),
            "success": (64, 192, 64),
            "error": (255, 64, 64),
            "warning": (255, 192, 64),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "gray": (128, 128, 128),
            "light_gray": (200, 200, 200),
            "dark_gray": (64, 64, 64),
            "input_bg": (240, 240, 240),
            "input_active": (255, 255, 255),
            "panel_bg": (40, 40, 40, 200)
        }
        
    def handle_event(self, event):
        """处理事件"""
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if self.current_screen != "main":
                    self.current_screen = "main"
                    self.clear_inputs()
                    return False
                else:
                    return True  # 返回主菜单
                    
            elif self.input_active:
                self.handle_input_event(event)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                return self.handle_click(event.pos)
                
        return False
    
    def handle_input_event(self, event):
        """处理输入事件"""
        if event.key == K_BACKSPACE:
            if self.input_fields[self.active_field]:
                self.input_fields[self.active_field] = self.input_fields[self.active_field][:-1]
        elif event.key == K_RETURN:
            self.submit_form()
        elif event.key == K_TAB:
            self.next_field()
        elif event.unicode.isprintable():
            if len(self.input_fields[self.active_field]) < 30:
                self.input_fields[self.active_field] += event.unicode
    
    def handle_click(self, pos):
        """处理鼠标点击"""
        x, y = pos
        screen_width = self.config.window.width
        screen_height = self.config.window.height
        
        if self.current_screen == "main":
            return self.handle_main_click(x, y)
        elif self.current_screen == "login":
            return self.handle_login_click(x, y)
        elif self.current_screen == "register":
            return self.handle_register_click(x, y)
        elif self.current_screen == "profile":
            return self.handle_profile_click(x, y)
        
        return False
    
    def handle_main_click(self, x, y):
        """处理主界面点击"""
        # 计算按钮位置
        screen_width = self.config.window.width
        center_x = screen_width // 2
        
        if self.network.is_logged_in():
            # 已登录状态的按钮
            profile_rect = pygame.Rect(center_x - 100, 200, 200, 40)
            logout_rect = pygame.Rect(center_x - 100, 250, 200, 40)
            start_rect = pygame.Rect(center_x - 100, 300, 200, 40)
            
            if profile_rect.collidepoint(x, y):
                self.current_screen = "profile"
            elif logout_rect.collidepoint(x, y):
                self.network.logout()
                self.show_message("已登出", self.colors["success"])
            elif start_rect.collidepoint(x, y):
                return True  # 开始游戏
        else:
            # 未登录状态的按钮
            login_rect = pygame.Rect(center_x - 100, 200, 200, 40)
            register_rect = pygame.Rect(center_x - 100, 250, 200, 40)
            guest_rect = pygame.Rect(center_x - 100, 300, 200, 40)
            
            if login_rect.collidepoint(x, y):
                self.current_screen = "login"
                self.input_active = True
                self.active_field = "username"
            elif register_rect.collidepoint(x, y):
                self.current_screen = "register"
                self.input_active = True
                self.active_field = "username"
            elif guest_rect.collidepoint(x, y):
                return True  # 游客模式开始游戏
        
        return False
    
    def handle_login_click(self, x, y):
        """处理登录界面点击"""
        center_x = self.config.window.width // 2
        
        # 输入框点击检测
        username_rect = pygame.Rect(center_x - 120, 200, 240, 30)
        password_rect = pygame.Rect(center_x - 120, 250, 240, 30)
        
        if username_rect.collidepoint(x, y):
            self.active_field = "username"
            self.input_active = True
        elif password_rect.collidepoint(x, y):
            self.active_field = "password"
            self.input_active = True
        else:
            # 按钮点击检测
            login_btn_rect = pygame.Rect(center_x - 80, 300, 160, 40)
            back_btn_rect = pygame.Rect(center_x - 80, 350, 160, 40)
            
            if login_btn_rect.collidepoint(x, y):
                self.submit_form()
            elif back_btn_rect.collidepoint(x, y):
                self.current_screen = "main"
                self.clear_inputs()
        
        return False
    
    def handle_register_click(self, x, y):
        """处理注册界面点击"""
        center_x = self.config.window.width // 2
        
        # 输入框点击检测
        username_rect = pygame.Rect(center_x - 120, 180, 240, 30)
        email_rect = pygame.Rect(center_x - 120, 220, 240, 30)
        password_rect = pygame.Rect(center_x - 120, 260, 240, 30)
        confirm_rect = pygame.Rect(center_x - 120, 300, 240, 30)
        
        if username_rect.collidepoint(x, y):
            self.active_field = "username"
            self.input_active = True
        elif email_rect.collidepoint(x, y):
            self.active_field = "email"
            self.input_active = True
        elif password_rect.collidepoint(x, y):
            self.active_field = "password"
            self.input_active = True
        elif confirm_rect.collidepoint(x, y):
            self.active_field = "confirm_password"
            self.input_active = True
        else:
            # 按钮点击检测
            register_btn_rect = pygame.Rect(center_x - 80, 350, 160, 40)
            back_btn_rect = pygame.Rect(center_x - 80, 400, 160, 40)
            
            if register_btn_rect.collidepoint(x, y):
                self.submit_form()
            elif back_btn_rect.collidepoint(x, y):
                self.current_screen = "main"
                self.clear_inputs()
        
        return False
    
    def handle_profile_click(self, x, y):
        """处理个人资料界面点击"""
        center_x = self.config.window.width // 2
        back_btn_rect = pygame.Rect(center_x - 80, 400, 160, 40)
        
        if back_btn_rect.collidepoint(x, y):
            self.current_screen = "main"
        
        return False
    
    def submit_form(self):
        """提交表单"""
        if self.current_screen == "login":
            self.do_login()
        elif self.current_screen == "register":
            self.do_register()
    
    def do_login(self):
        """执行登录"""
        username = self.input_fields["username"].strip()
        password = self.input_fields["password"].strip()
        
        if not username or not password:
            self.show_message("请填写用户名和密码", self.colors["error"])
            return
        
        result = self.network.login(username, password)
        if result["success"]:
            self.show_message(f"欢迎回来, {username}!", self.colors["success"])
            self.current_screen = "main"
            self.clear_inputs()
        else:
            self.show_message(result["message"], self.colors["error"])
    
    def do_register(self):
        """执行注册"""
        username = self.input_fields["username"].strip()
        email = self.input_fields["email"].strip()
        password = self.input_fields["password"].strip()
        confirm = self.input_fields["confirm_password"].strip()
        
        if not all([username, email, password, confirm]):
            self.show_message("请填写所有字段", self.colors["error"])
            return
        
        if password != confirm:
            self.show_message("两次输入的密码不一致", self.colors["error"])
            return
        
        if len(password) < 6:
            self.show_message("密码长度至少6位", self.colors["error"])
            return
        
        result = self.network.register(username, password, email)
        if result["success"]:
            self.show_message("注册成功！请登录", self.colors["success"])
            self.current_screen = "login"
            self.clear_inputs()
        else:
            self.show_message(result["message"], self.colors["error"])
    
    def next_field(self):
        """切换到下一个输入框"""
        if self.current_screen == "login":
            fields = ["username", "password"]
        elif self.current_screen == "register":
            fields = ["username", "email", "password", "confirm_password"]
        else:
            return
        
        try:
            current_index = fields.index(self.active_field)
            next_index = (current_index + 1) % len(fields)
            self.active_field = fields[next_index]
        except ValueError:
            self.active_field = fields[0]
    
    def clear_inputs(self):
        """清空输入框"""
        self.input_fields = {key: "" for key in self.input_fields}
        self.active_field = "username"
        self.input_active = False
    
    def show_message(self, text, color):
        """显示消息"""
        self.message = text
        self.message_color = color
        # 3秒后清空消息
        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)
    
    def render(self, screen):
        """渲染界面"""
        # 创建半透明背景
        overlay = pygame.Surface((self.config.window.width, self.config.window.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 创建主面板
        panel_width = 300
        panel_height = 500
        panel_x = (self.config.window.width - panel_width) // 2
        panel_y = (self.config.window.height - panel_height) // 2
        
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill(self.colors["panel_bg"])
        screen.blit(panel, (panel_x, panel_y))
        
        if self.current_screen == "main":
            self.render_main_screen(screen)
        elif self.current_screen == "login":
            self.render_login_screen(screen)
        elif self.current_screen == "register":
            self.render_register_screen(screen)
        elif self.current_screen == "profile":
            self.render_profile_screen(screen)
        
        # 渲染消息
        if self.message:
            self.render_message(screen)
    
    def render_main_screen(self, screen):
        """渲染主界面"""
        center_x = self.config.window.width // 2
        
        # 标题
        if self.network.is_logged_in():
            user_info = self.network.get_user_info()
            title_text = self.title_font.render(f"欢迎, {user_info['username']}", True, self.colors["white"])
        else:
            title_text = self.title_font.render("用户登录", True, self.colors["white"])
        
        title_rect = title_text.get_rect(center=(center_x, 150))
        screen.blit(title_text, title_rect)
        
        # 网络状态指示
        status_color = self.colors["success"] if self.network.is_online else self.colors["error"]
        status_text = "在线" if self.network.is_online else "离线"
        status_surface = self.message_font.render(f"服务器: {status_text}", True, status_color)
        status_rect = status_surface.get_rect(center=(center_x, 175))
        screen.blit(status_surface, status_rect)
        
        # 按钮
        if self.network.is_logged_in():
            self.render_button(screen, "个人资料", center_x - 100, 200, 200, 40)
            self.render_button(screen, "登出", center_x - 100, 250, 200, 40)
            self.render_button(screen, "开始游戏", center_x - 100, 300, 200, 40, self.colors["primary"])
        else:
            self.render_button(screen, "登录", center_x - 100, 200, 200, 40)
            self.render_button(screen, "注册", center_x - 100, 250, 200, 40)
            self.render_button(screen, "游客模式", center_x - 100, 300, 200, 40, self.colors["secondary"])
    
    def render_login_screen(self, screen):
        """渲染登录界面"""
        center_x = self.config.window.width // 2
        
        # 标题
        title_text = self.title_font.render("用户登录", True, self.colors["white"])
        title_rect = title_text.get_rect(center=(center_x, 150))
        screen.blit(title_text, title_rect)
        
        # 输入框
        self.render_input_field(screen, "用户名", "username", center_x - 120, 200, 240, 30)
        self.render_input_field(screen, "密码", "password", center_x - 120, 250, 240, 30, password=True)
        
        # 按钮
        self.render_button(screen, "登录", center_x - 80, 300, 160, 40, self.colors["primary"])
        self.render_button(screen, "返回", center_x - 80, 350, 160, 40, self.colors["secondary"])
    
    def render_register_screen(self, screen):
        """渲染注册界面"""
        center_x = self.config.window.width // 2
        
        # 标题
        title_text = self.title_font.render("用户注册", True, self.colors["white"])
        title_rect = title_text.get_rect(center=(center_x, 130))
        screen.blit(title_text, title_rect)
        
        # 输入框
        self.render_input_field(screen, "用户名", "username", center_x - 120, 180, 240, 30)
        self.render_input_field(screen, "邮箱", "email", center_x - 120, 220, 240, 30)
        self.render_input_field(screen, "密码", "password", center_x - 120, 260, 240, 30, password=True)
        self.render_input_field(screen, "确认密码", "confirm_password", center_x - 120, 300, 240, 30, password=True)
        
        # 按钮
        self.render_button(screen, "注册", center_x - 80, 350, 160, 40, self.colors["primary"])
        self.render_button(screen, "返回", center_x - 80, 400, 160, 40, self.colors["secondary"])
    
    def render_profile_screen(self, screen):
        """渲染个人资料界面"""
        center_x = self.config.window.width // 2
        user_info = self.network.get_user_info()
        
        if not user_info:
            return
        
        # 标题
        title_text = self.title_font.render("个人资料", True, self.colors["white"])
        title_rect = title_text.get_rect(center=(center_x, 130))
        screen.blit(title_text, title_rect)
        
        # 用户信息
        y_pos = 180
        info_items = [
            f"用户名: {user_info['username']}",
            f"邮箱: {user_info['email']}",
            f"最佳分数: {user_info.get('best_score', 0)}分",
            f"总分数: {user_info.get('total_score', 0)}分",
            f"游戏次数: {user_info.get('games_played', 0)}次"
        ]
        
        for item in info_items:
            text_surface = self.input_font.render(item, True, self.colors["white"])
            text_rect = text_surface.get_rect(center=(center_x, y_pos))
            screen.blit(text_surface, text_rect)
            y_pos += 30
        
        # 返回按钮
        self.render_button(screen, "返回", center_x - 80, 400, 160, 40, self.colors["secondary"])
    
    def render_input_field(self, screen, label, field_name, x, y, width, height, password=False):
        """渲染输入框"""
        # 标签
        label_surface = self.input_font.render(label + ":", True, self.colors["white"])
        screen.blit(label_surface, (x, y - 25))
        
        # 输入框背景
        is_active = self.active_field == field_name and self.input_active
        bg_color = self.colors["input_active"] if is_active else self.colors["input_bg"]
        border_color = self.colors["primary"] if is_active else self.colors["gray"]
        
        pygame.draw.rect(screen, bg_color, (x, y, width, height))
        pygame.draw.rect(screen, border_color, (x, y, width, height), 2)
        
        # 输入文本
        text = self.input_fields[field_name]
        if password and text:
            display_text = "*" * len(text)
        else:
            display_text = text
        
        if len(display_text) > 20:
            display_text = display_text[-20:]  # 只显示最后20个字符
        
        text_surface = self.input_font.render(display_text, True, self.colors["black"])
        screen.blit(text_surface, (x + 5, y + 5))
        
        # 光标
        if is_active:
            cursor_x = x + 5 + text_surface.get_width()
            pygame.draw.line(screen, self.colors["black"], (cursor_x, y + 5), (cursor_x, y + height - 5), 1)
    
    def render_button(self, screen, text, x, y, width, height, color=None):
        """渲染按钮"""
        if color is None:
            color = self.colors["gray"]
        
        # 按钮背景
        pygame.draw.rect(screen, color, (x, y, width, height))
        pygame.draw.rect(screen, self.colors["white"], (x, y, width, height), 2)
        
        # 按钮文本
        text_surface = self.button_font.render(text, True, self.colors["white"])
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text_surface, text_rect)
    
    def render_message(self, screen):
        """渲染消息"""
        if self.message:
            center_x = self.config.window.width // 2
            message_surface = self.message_font.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(center_x, 50))
            
            # 消息背景
            bg_rect = message_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(screen, self.message_color, bg_rect, 2)
            
            screen.blit(message_surface, message_rect) 