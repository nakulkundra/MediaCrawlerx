import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium font-mono ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default:
          'bg-cyber-neon-cyan text-cyber-bg-primary font-semibold hover:bg-cyber-neon-cyan/90 shadow-glow-cyan-sm hover:shadow-glow-cyan',
        destructive:
          'bg-cyber-neon-pink text-white font-semibold hover:bg-cyber-neon-pink/90 shadow-glow-pink-sm hover:shadow-glow-pink',
        outline:
          'border border-cyber-border-DEFAULT bg-cyber-bg-panel hover:bg-cyber-bg-elevated hover:text-cyber-neon-cyan hover:border-cyber-neon-cyan/50 text-cyber-text-primary',
        secondary:
          'bg-cyber-bg-tertiary text-cyber-text-primary hover:bg-cyber-bg-elevated border border-cyber-border-subtle',
        ghost:
          'hover:bg-cyber-bg-elevated hover:text-cyber-neon-cyan text-cyber-text-secondary',
        link:
          'text-cyber-neon-cyan underline-offset-4 hover:underline',
        glow:
          'bg-cyber-neon-cyan/20 border border-cyber-neon-cyan text-cyber-neon-cyan hover:bg-cyber-neon-cyan/30 shadow-glow-cyan-sm hover:shadow-glow-cyan',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 rounded-md px-3 text-xs',
        lg: 'h-12 rounded-md px-8 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
