import { useTranslation } from 'react-i18next'
import { AlertTriangle, ShieldCheck, Github, FileText, Check, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

const LICENSE_KEY = 'mediacrawler_license_accepted'

export function isLicenseAccepted(): boolean {
  return localStorage.getItem(LICENSE_KEY) === 'true'
}

export function clearLicense(): void {
  localStorage.removeItem(LICENSE_KEY)
}

interface LicenseDisclaimerProps {
  onAccept: () => void
}

export function LicenseDisclaimer({ onAccept }: LicenseDisclaimerProps) {
  const { t } = useTranslation('license')

  const handleAccept = () => {
    localStorage.setItem(LICENSE_KEY, 'true')
    onAccept()
  }

  const handleDecline = () => {
    window.location.href = 'https://github.com/NanmiCoder/MediaCrawler'
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-cyber-bg-panel border border-cyber-border-DEFAULT rounded-lg shadow-cyber-card max-w-lg w-full relative overflow-hidden">
        {/* Corner decorations */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-cyber-neon-cyan" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyber-neon-cyan" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyber-neon-cyan" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-cyber-neon-cyan" />

        {/* Header */}
        <div className="p-6 pb-4 border-b border-cyber-border-subtle bg-cyber-bg-tertiary/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-cyber-neon-orange/10 border border-cyber-neon-orange/30 text-cyber-neon-orange">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-mono font-bold text-cyber-text-primary">
                {t('title')}
              </h2>
              <p className="text-xs text-cyber-neon-orange font-mono">
                {t('warning')}
              </p>
            </div>
          </div>
        </div>

        {/* Body content */}
        <div className="p-6 space-y-4 font-mono text-xs">
          <div className="space-y-2.5 text-cyber-text-secondary bg-cyber-bg-tertiary/20 p-4 rounded-lg border border-cyber-border-subtle">
            <div className="flex items-start gap-2">
              <span className="text-cyber-neon-cyan font-bold">1.</span>
              <span>{t('content.line1')}</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-cyber-neon-cyan font-bold">2.</span>
              <span>{t('content.line2')}</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-cyber-neon-cyan font-bold">3.</span>
              <span>{t('content.line3')}</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="text-cyber-neon-cyan font-bold">4.</span>
              <span>{t('content.line4')}</span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <a
              href="https://github.com/NanmiCoder/MediaCrawler/blob/main/LICENSE"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-cyber-neon-cyan hover:underline"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>{t('license')}</span>
            </a>
            <a
              href="https://github.com/NanmiCoder/MediaCrawler"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-cyber-text-muted hover:text-cyber-text-primary"
            >
              <Github className="w-3.5 h-3.5" />
              <span>{t('github')}</span>
            </a>
          </div>
        </div>

        {/* Footer buttons */}
        <div className="p-6 pt-0 flex gap-3">
          <Button
            variant="outline"
            className="flex-1 font-mono text-xs"
            onClick={handleDecline}
          >
            <X className="w-4 h-4 mr-1 text-cyber-neon-pink" />
            {t('decline')}
          </Button>
          <Button
            variant="glow"
            className="flex-1 font-mono text-xs bg-cyber-neon-cyan text-cyber-bg-primary font-bold hover:bg-cyber-neon-cyan/90"
            onClick={handleAccept}
          >
            <Check className="w-4 h-4 mr-1" />
            {t('confirm')}
          </Button>
        </div>
      </div>
    </div>
  )
}
