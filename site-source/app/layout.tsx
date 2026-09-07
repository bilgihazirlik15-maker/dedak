import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'Anasayfa | DEDAK',
  description: 'DEDAK dil eğitimi akreditasyonu, değerlendirme ölçütleri, başvuru bilgileri ve kurumsal belgeler.',
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="tr"><body>{children}<script src="assets/site.js" defer /></body></html>;
}
