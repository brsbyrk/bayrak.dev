---
layout: ../../layouts/project.astro
title: "Remage: Simplifying Image Resizing and Watermarking"
pubDate: 2024-11-12
description: "A look into building Remage, an easy-to-use desktop app for image resizing and watermarking."
author: "Baris Bayrak"
excerpt: Remage is a cross-platform app I’ve been developing to streamline basic image processing tasks, like resizing and watermarking. Built with performance and simplicity in mind, it's a tool designed to be lightweight, efficient, and effective.
image:
  src: /remage-logo.png
  alt: Screenshot of Remage app interface
tags: ["project", "desktop app", "image processing", "Rust", "Tauri"]
---

# Remage: Simplifying Image Resizing and Watermarking

In the past few months, I’ve been working on a side project called **Remage** — a cross-platform desktop app focused on providing a simple solution for image resizing and watermarking. The idea for Remage came from my own experience needing a quick, easy-to-use tool for basic image tasks without dealing with large, complex software.

## Why I Built Remage

As someone who often works with images, I noticed a gap in the available tools: existing software was either overly complex or lacked the exact simplicity I wanted. I wanted something that sits quietly in the system tray, ready whenever I need it, with just enough features to get the job done efficiently. That’s how Remage was born — a lightweight app that minimizes the fuss of image editing.

## What Remage Can Do

Here’s a rundown of Remage’s key features:

- **Quick Image Resizing**: Just drag and drop an image, choose a preset, and it’s instantly resized.
- **Watermarking**: Add custom watermarks to your images. You can control the style, position, and opacity, keeping it versatile for different needs.
- **Custom Presets**: Set up your favorite presets for resizing and watermarking, making your workflow even faster.
- **Cross-Platform Support**: Remage is designed for both Windows and macOS, so it’s there for you no matter your platform.

## The Tech Behind Remage

For Remage, I wanted to prioritize performance and cross-platform compatibility. The backend is built using **Rust** using Tauri. This way, the app remains lightweight while handling tasks efficiently. The frontend is built with **React** and **Tailwind** keeping the UI sleek and responsive.

## Challenges and Lessons Learned

Developing Remage has been a learning journey in many ways. From exploring image processing with Rust to designing a minimalist user interface, each part of the project brought new insights. One of the most interesting challenges was optimizing image resizing performance and ensuring that the app ran smoothly without using too many resources.

I’ve also gained a lot of experience in balancing functionality and simplicity. The goal was to keep Remage intuitive for everyday users, so I had to think carefully about which features to include and how to make them as accessible as possible.

## Planned Features

I’m constantly thinking about ways to improve Remage. Some ideas I have for future updates include:

- **Video Support**: Extending Remage to handle video resizing and watermarking.
- **Batch Processing**: Allowing multiple images to be processed at once.
- **Enhanced Export Options**: Adding more export settings for users who need advanced customization.

## My Development Journey with Remage

Building Remage has been both challenging and rewarding. It’s my take on what a lightweight, user-friendly image processing app should be, and I hope it can help others as much as it’s helped me. This project is still a work in progress, and I’m excited to keep refining it.

If you’re interested in trying out Remage or have feedback and suggestions, feel free to reach out. I’d love to hear your thoughts and continue improving the app based on real user input.

---

Thank you for reading, and stay tuned for more updates on Remage!
