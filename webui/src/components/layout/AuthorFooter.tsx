import { useTranslation } from 'react-i18next'
import { Sparkles, Heart } from 'lucide-react'

export function AuthorFooter() {
  const { t } = useTranslation('license')

  return (
    <footer className="h-24 flex-shrink-0 glass-panel border-t border-cyber-border-subtle">
      <div className="h-full px-6 flex items-center justify-center gap-6">
        {/* Author Avatar */}
        <div className="w-14 h-14 rounded-lg overflow-hidden border-2 border-cyber-neon-cyan/60 flex-shrink-0 shadow-glow-cyan-sm">
          <img
            src="/logos/my_logo.png"
            alt="Relakkes"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Author Info */}
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-cyber-text-primary">
              {t('author.name')}
            </span>
            <Sparkles className="w-5 h-5 text-cyber-neon-cyan animate-pulse" />
          </div>
          <span className="text-sm text-cyber-text-muted hidden sm:inline">
            {t('author.description')}
          </span>
          <div className="flex items-center gap-2 text-cyber-neon-cyan">
            <Heart className="w-4 h-4 fill-current animate-pulse" />
            <span className="text-sm font-medium">
              {t('author.slogan')}
            </span>
          </div>
        </div>

        {/* Social Links */}
        <div className="flex items-center gap-3">
          <a
            href="https://github.com/NanmiCoder"
            target="_blank"
            rel="noopener noreferrer"
            className="w-10 h-10 rounded-lg bg-cyber-bg-tertiary border border-cyber-border-subtle hover:border-cyber-neon-cyan flex items-center justify-center transition-all hover:scale-105"
            title="GitHub"
          >
            <img src="/logos/github.png" alt="GitHub" className="w-5 h-5" />
          </a>
          <a
            href="https://space.bilibili.com/434377496"
            target="_blank"
            rel="noopener noreferrer"
            className="w-10 h-10 rounded-lg bg-cyber-bg-tertiary border border-cyber-border-subtle hover:border-cyber-neon-cyan flex items-center justify-center transition-all hover:scale-105"
            title="Bilibili"
          >
            <img src="/logos/bilibili_logo.png" alt="Bilibili" className="w-5 h-5" />
          </a>
          <a
            href="https://www.xiaohongshu.com/user/profile/5b8a6a24e4bbc200010c7bf3"
            target="_blank"
            rel="noopener noreferrer"
            className="w-10 h-10 rounded-lg bg-cyber-bg-tertiary border border-cyber-border-subtle hover:border-cyber-neon-cyan flex items-center justify-center transition-all hover:scale-105"
            title="Xiaohongshu"
          >
            <img src="/logos/xiaohongshu_logo.png" alt="Xiaohongshu" className="w-5 h-5" />
          </a>
          <a
            href="https://www.douyin.com/user/MS4wLjABAAAAxxx"
            target="_blank"
            rel="noopener noreferrer"
            className="w-10 h-10 rounded-lg bg-cyber-bg-tertiary border border-cyber-border-subtle hover:border-cyber-neon-cyan flex items-center justify-center transition-all hover:scale-105"
            title="Douyin"
          >
            <img src="/logos/douyin.png" alt="Douyin" className="w-5 h-5" />
          </a>
        </div>
      </div>
    </footer>
  )
}
