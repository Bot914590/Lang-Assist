import { copyFileSync, mkdirSync, existsSync, readdirSync, rmSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const distDir = join(__dirname, '..', 'dist');
const publicDir = join(__dirname, '..', 'public');

// Создаем папку для иконок в dist и копируем все файлы
const iconsDir = join(distDir, 'icons');

if (!existsSync(iconsDir)) {
  mkdirSync(iconsDir, { recursive: true });
}

const publicIconsDir = join(publicDir, 'icons');

if (existsSync(publicIconsDir)) {
  const files = readdirSync(publicIconsDir);
  console.log(`Найдены файлы в public/icons: ${files.join(', ')}`);
  files.forEach(file => {
    if (file.endsWith('.svg')) {
      const src = join(publicIconsDir, file);
      const dest = join(iconsDir, file);
      copyFileSync(src, dest);
      console.log(`✓ Скопирован ${file}`);
    }
  });
}

// Копируем manifest.json в конце (после иконок)
const manifestSrc = join(publicDir, 'manifest.json');
const manifestDest = join(distDir, 'manifest.json');

if (existsSync(manifestSrc)) {
  copyFileSync(manifestSrc, manifestDest);
  console.log('✓ manifest.json скопирован в dist/');
}

console.log('✓ Ассеты скопированы');
