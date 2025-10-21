import Link from "next/link";
import { IconLink } from "../ui/IconLink";

export default function Header() {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="container flex items-center justify-between py-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-md bg-brand"></div>
          <span className="text-lg font-semibold tracking-tight text-ink">Blake Inc.</span>
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/legal/disclaimer" className="text-sm text-ink-light hover:text-ink">
            Disclaimer
          </Link>
          <div className="hidden md:flex items-center gap-2">
            <IconLink href="https://github.com" type="github" ariaLabel="GitHub" />
            <IconLink href="https://twitter.com" type="twitter" ariaLabel="Twitter" />
            <IconLink href="https://www.linkedin.com" type="linkedin" ariaLabel="LinkedIn" />
          </div>
        </nav>
      </div>
    </header>
  );
}