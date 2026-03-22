/**
 * Markdown 渲染工具模块
 * 
 * 功能说明：
 * - 使用 markdown-it 库将 Markdown 文本转换为 HTML
 * - 配置选项：禁用 HTML 标签、支持链接识别、转换换行符
 * 
 * 使用场景：
 * - MessageBubble 组件中渲染用户/助手的 Markdown 消息
 * - 支持标题、列表、代码块、链接等常见 Markdown 语法
 */

import MarkdownIt from "markdown-it";

// 创建 markdown-it 实例，配置渲染选项
const markdown = new MarkdownIt({
  html: false,          // 禁用 HTML 标签输入（防止 XSS）
  linkify: true,        // 自动识别 URL 并转换为链接
  breaks: true,         // 将换行符转换为 <br>
});

/**
 * 渲染 Markdown 文本为 HTML
 * @param content - 原始 Markdown 文本
 * @returns 渲染后的 HTML 字符串
 */
export function renderMarkdown(content: string) {
  return markdown.render(content);
}
