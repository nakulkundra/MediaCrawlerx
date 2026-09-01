import { Sun, Moon, Monitor } from 'lucide-react'
import { useThemeStore } from '@/store/themeStore'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

type Theme = 'light' | 'dark' | 'system'

const themes: { value: Theme; label: string; icon: typeof Sun }[] = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'Auto', icon: Monitor },
]

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore()

  const currentTheme = themes.find(t => t.value === theme) || themes[0]
  const Icon = currentTheme.icon

  return (
    <Select value={theme} onValueChange={(v) => setTheme(v as Theme)}>
      <SelectTrigger className="h-8 px-2 text-xs font-mono bg-cyber-bg-panel border-cyber-border-DEFAULT hover:border-cyber-neon-cyan/50 text-cyber-text-secondary hover:text-cyber-text-primary gap-1.5 focus:ring-0 focus:ring-offset-0">
        <Icon className="w-3.5 h-3.5 text-cyber-neon-cyan" />
        <SelectValue placeholder={currentTheme.label} />
      </SelectTrigger>
      <SelectContent className="bg-cyber-bg-panel border-cyber-border-DEFAULT">
        {themes.map((t) => {
          const ItemIcon = t.icon
          return (
            <SelectItem
              key={t.value}
              value={t.value}
              className="text-xs font-mono text-cyber-text-secondary hover:text-cyber-text-primary hover:bg-cyber-bg-elevated cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <ItemIcon className="w-3.5 h-3.5 text-cyber-neon-cyan" />
                <span>{t.label}</span>
              </div>
            </SelectItem>
          )
        })}
      </SelectContent>
    </Select>
  )
}
