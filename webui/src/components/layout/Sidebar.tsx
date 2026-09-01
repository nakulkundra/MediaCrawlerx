import { Bug, Wifi, AlertTriangle, Github } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { useCrawlerStore } from '@/store/crawlerStore'
import { useCrawlerStatus } from '@/hooks/useCrawler'
import { LanguageSwitch } from './LanguageSwitch'
import { ThemeToggle } from './ThemeToggle'

interface SidebarProps {
  onShowDisclaimer?: () => void
}

export function Sidebar({ onShowDisclaimer }: SidebarProps) {
  const { t } = useTranslation()
  const { t: tLicense } = useTranslation('license')
  const status = useCrawlerStore((state) => state.status)

  // Poll status
  useCrawlerStatus()

  const isRunning = status === 'running'

  return (
    <header className="h-14 flex-shrink-0 glass-panel border-b border-cyber-border-subtle relative z-10">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Left: Logo and GitHub Star */}
        <div className="flex items-center gap-3">
          <Bug className="w-5 h-5 text-cyber-neon-cyan" />
          <span className="font-mono font-bold text-cyber-text-primary tracking-wider text-sm">
            MediaCrawler
          </span>
          <a
            href="https://github.com/NanmiCoder/MediaCrawler"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyber-bg-tertiary border border-cyber-border-subtle hover:border-cyber-neon-cyan text-xs font-mono text-cyber-text-secondary hover:text-cyber-text-primary transition-all ml-2"
          >
            <Github className="w-3.5 h-3.5" />
            <span>GitHub</span>
          </a>
        </div>

        {/* Right: Status, Controls, Language & Theme */}
        <div className="flex items-center gap-3">
          {/* Status badge */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-cyber-bg-tertiary border border-cyber-border-subtle font-mono text-xs">
            <div className={`status-dot ${isRunning ? 'status-dot-online' : 'status-dot-offline'}`} />
            <span className="text-cyber-text-secondary">
              {isRunning ? t('status.running') : t('status.idle')}
            </span>
          </div>

          {/* License / Disclaimer trigger */}
          {onShowDisclaimer && (
            <button
              type="button"
              onClick={onShowDisclaimer}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-cyber-bg-tertiary border border-cyber-border-subtle hover:border-cyber-neon-orange text-xs font-mono text-cyber-neon-orange transition-all"
              title={t('sidebar.disclaimer')}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{t('sidebar.license')}</span>
            </button>
          )}

          {/* Language Switch */}
          <LanguageSwitch />

          {/* Theme Toggle */}
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
