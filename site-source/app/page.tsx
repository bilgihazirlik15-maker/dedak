import { homeContent } from './home-content';
export default function Home() {
  return <div dangerouslySetInnerHTML={{ __html: homeContent }} />;
}
