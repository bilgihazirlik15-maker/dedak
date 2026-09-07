from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent/'site-source'
(ROOT/'app/page.tsx').write_text('''import { homeContent } from './home-content';
export default function Home() {
  return <div dangerouslySetInnerHTML={{ __html: homeContent }} />;
}
''',encoding='utf-8')
(ROOT/'app/layout.tsx').write_text('''import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'Dil eğitiminde kalite güvencesi | DEDAK',
  description: 'DEDAK dil eğitimi akreditasyonu, değerlendirme ölçütleri, başvuru bilgileri ve kurumsal belgeler.',
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="tr"><body>{children}<script src="assets/site.js" defer /></body></html>;
}
''',encoding='utf-8')
(ROOT/'next.config.ts').write_text('''import type { NextConfig } from 'next';
const nextConfig: NextConfig = { output: 'export' };
export default nextConfig;
''',encoding='utf-8')
(ROOT/'vite.config.ts').write_text('''import { sites } from '@openai/sites-vite-plugin';
import vinext from 'vinext';
import { defineConfig } from 'vite';
// Portable static website without a server runtime or hosting-specific bindings.
export default defineConfig({ plugins: [vinext(), sites()] });
''',encoding='utf-8')
(ROOT/'.openai/hosting.json').write_text('{"d1":null,"r2":null,"static":{"directory":"dist/client"}}\n',encoding='utf-8')
