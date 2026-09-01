import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold font-mono transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-cyber-neon-cyan/20 text-cyber-neon-cyan border-cyber-neon-cyan/40 shadow-glow-cyan-sm',
        secondary:
          'border-transparent bg-cyber-bg-tertiary text-cyber-text-secondary',
        destructive:
          'border-transparent bg-cyber-neon-pink/20 text-cyber-neon-pink border-cyber-neon-pink/40 shadow-glow-pink-sm',
        outline:
          'border-cyber-border-DEFAULT text-cyber-text-primary',
        glow:
          'border-cyber-neon-cyan bg-cyber-neon-cyan/10 text-cyber-neon-cyan shadow-glow-cyan',
        success:
          'border-cyber-neon-green/40 bg-cyber-neon-green/20 text-cyber-neon-green shadow-glow-green-sm',
        warning:
          'border-cyber-neon-orange/40 bg-cyber-neon-orange/20 text-cyber-neon-orange',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
