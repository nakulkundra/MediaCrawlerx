import { Globe } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const languages = [
  { code: 'zh-CN', label: '中文' },
  { code: 'en-US', label: 'English' },
]

export function LanguageSwitch() {
  const { i18n } = useTranslation()

  const currentLang = languages.find(l => l.code === i18n.language) || languages[1]

  return (
    <Select value={i18n.language} onValueChange={(lang) => i18n.changeLanguage(lang)}>
      <SelectTrigger className="h-8 px-2 text-xs font-mono bg-cyber-bg-panel border-cyber-border-DEFAULT hover:border-cyber-neon-cyan/50 text-cyber-text-secondary hover:text-cyber-text-primary gap-1.5 focus:ring-0 focus:ring-offset-0">
        <Globe className="w-3.5 h-3.5 text-cyber-neon-cyan" />
        <SelectValue placeholder={currentLang.label} />
      </SelectTrigger>
      <SelectContent className="bg-cyber-bg-panel border-cyber-border-DEFAULT">
        {languages.map((lang) => (
          <SelectItem
            key={lang.code}
            value={lang.code}
            className="text-xs font-mono text-cyber-text-secondary hover:text-cyber-text-primary hover:bg-cyber-bg-elevated cursor-pointer"
          >
            {lang.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
