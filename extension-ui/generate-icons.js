import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join, dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Project root - это extension-ui (где находится этот скрипт)
const projectRoot = __dirname;
console.log('Project root:', projectRoot);

// Простая SVG иконка для разных размеров
function createIconSVG(size) {
  const colors = {
    16: '#3b82f6',
    48: '#2563eb',
    128: '#1d4ed8'
  };

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}">
    <defs>
      <linearGradient id="grad${size}" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${colors[size]};stop-opacity:1" />
        <stop offset="100%" style="stop-color:${colors[size]};stop-opacity:0.8" />
      </linearGradient>
    </defs>
    <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 1}" fill="url(#grad${size})"/>
    <text x="${size/2}" y="${size * 0.65}" font-family="Arial, sans-serif" font-size="${size * 0.5}" font-weight="bold" fill="white" text-anchor="middle">L</text>
  </svg>`;
}

// Создаем SVG иконки
const iconsDir = join(projectRoot, 'public', 'icons');
console.log('Icons directory:', iconsDir);

mkdirSync(iconsDir, { recursive: true });

const sizes = [16, 48, 128];

sizes.forEach(size => {
  const svg = createIconSVG(size);
  const filename = `icon${size}.svg`;
  const filepath = join(iconsDir, filename);
  
  console.log(`Writing ${filepath}...`);
  writeFileSync(filepath, svg);
  
  if (existsSync(filepath)) {
    console.log(`✓ Создана иконка ${filename}`);
  } else {
    console.log(`✗ Ошибка создания ${filename}`);
  }
});

// Обновляем manifest.json
const manifestPath = join(projectRoot, 'public', 'manifest.json');
console.log('Manifest path:', manifestPath);

const manifest = {
  manifest_version: 3,
  name: "Language Assist",
  version: "1.0.0",
  description: "Приложение для изучения языков с анализом текстов",
  permissions: ["storage", "identity"],
  action: {
    default_popup: "index.html",
    default_title: "Language Assist",
    default_icon: {
      "16": "icons/icon16.svg",
      "48": "icons/icon48.svg",
      "128": "icons/icon128.svg"
    }
  },
  icons: {
    "16": "icons/icon16.svg",
    "48": "icons/icon48.svg",
    "128": "icons/icon128.svg"
  },
  content_security_policy: {
    extension_pages: "script-src 'self'; object-src 'self'"
  }
};

writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));

console.log('✓ manifest.json обновлен для SVG иконок');
console.log('✓ Готово!');
