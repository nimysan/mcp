import { NextResponse } from 'next/server';
import * as cheerio from 'cheerio';

const FETCH_TIMEOUT = 5000; // 5 seconds timeout

async function fetchWithTimeout(url: string): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
  
  try {
    const response = await fetch(url, { 
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; ProductBot/1.0)'
      }
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function POST(request: Request) {
  try {
    const { url } = await request.json();

    // 获取网页内容
    const response = await fetchWithTimeout(url);
    const html = await response.text();

    // 使用 cheerio 解析 HTML
    const $ = cheerio.load(html);

    // 尝试获取标题
    const title = 
      $('meta[property="og:title"]').attr('content') ||
      $('meta[name="twitter:title"]').attr('content') ||
      $('title').text() ||
      new URL(url).hostname;

    // 尝试获取图片
    let image = 
      $('meta[property="og:image"]').attr('content') ||
      $('meta[name="twitter:image"]').attr('content') ||
      $('link[rel="icon"]').attr('href') ||
      '';

    // 如果找到相对路径的图片，转换为绝对路径
    if (image && !image.startsWith('http')) {
      const baseUrl = new URL(url);
      image = new URL(image, baseUrl.origin).toString();
    }

    return NextResponse.json({
      title: title.trim(),
      image: image
    });
  } catch (error) {
    console.error('Error fetching product info:', error);
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Request timeout' },
        { status: 408 }
      );
    }
    return NextResponse.json(
      { error: 'Failed to fetch product info' },
      { status: 500 }
    );
  }
}
