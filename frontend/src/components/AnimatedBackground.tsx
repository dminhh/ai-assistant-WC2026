"use client"
import { useEffect, useRef } from "react"

interface Particle {
  x: number; y: number; size: number
  speedY: number; speedX: number
  opacity: number; opacityDelta: number; color: string
}

const COLORS = ["rgba(255,215,0,", "rgba(255,235,100,", "rgba(255,200,50,"]

export function AnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mouseRef  = useRef<{ x: number; y: number }>({ x: -9999, y: -9999 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animId: number
    let particles: Particle[] = []
    let breatheT = 0

    function onMouseMove(e: MouseEvent) {
      mouseRef.current = { x: e.clientX, y: e.clientY }
    }
    window.addEventListener("mousemove", onMouseMove)

    function resize() {
      if (!canvas) return
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    function spawnParticle(): Particle {
      if (!canvas) return {} as Particle
      return {
        x: Math.random() * canvas.width,
        y: canvas.height + Math.random() * 100,
        size: Math.random() * 2.2 + 0.6,
        speedY: Math.random() * 0.5 + 0.2,
        speedX: (Math.random() - 0.5) * 0.25,
        opacity: 0,
        opacityDelta: Math.random() * 0.004 + 0.002,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
      }
    }

    function init() {
      if (!canvas) return
      particles = Array.from({ length: 120 }, () => {
        const p = spawnParticle()
        p.y = Math.random() * canvas.height
        p.opacity = Math.random() * 0.5
        return p
      })
    }

    function drawPitch() {
      if (!canvas || !ctx) return
      const W = canvas.width
      const H = canvas.height

      // Scale pitch to fill most of the screen
      const pw = W * 0.88
      const ph = H * 0.80
      const px = (W - pw) / 2
      const py = (H - ph) / 2 + H * 0.06

      ctx.save()
      ctx.strokeStyle = "rgba(255,255,255,0.13)"
      ctx.lineWidth = 1

      // Outer rectangle
      ctx.strokeRect(px, py, pw, ph)

      // Center line
      ctx.beginPath()
      ctx.moveTo(W / 2, py)
      ctx.lineTo(W / 2, py + ph)
      ctx.stroke()

      // Center circle
      ctx.beginPath()
      ctx.arc(W / 2, py + ph / 2, ph * 0.14, 0, Math.PI * 2)
      ctx.stroke()

      // Center dot
      ctx.beginPath()
      ctx.arc(W / 2, py + ph / 2, 2.5, 0, Math.PI * 2)
      ctx.fillStyle = "rgba(255,255,255,0.15)"
      ctx.fill()

      // Left penalty box
      const pbW = pw * 0.16
      const pbH = ph * 0.44
      ctx.strokeRect(px, py + (ph - pbH) / 2, pbW, pbH)

      // Left 6-yard box
      const gbW = pw * 0.065
      const gbH = ph * 0.22
      ctx.strokeRect(px, py + (ph - gbH) / 2, gbW, gbH)

      // Left penalty spot
      ctx.beginPath()
      ctx.arc(px + pw * 0.115, py + ph / 2, 2, 0, Math.PI * 2)
      ctx.fillStyle = "rgba(255,255,255,0.15)"
      ctx.fill()

      // Left penalty arc
      ctx.beginPath()
      ctx.arc(px + pw * 0.115, py + ph / 2, ph * 0.14, -Math.PI * 0.38, Math.PI * 0.38)
      ctx.stroke()

      // Right penalty box
      ctx.strokeRect(px + pw - pbW, py + (ph - pbH) / 2, pbW, pbH)

      // Right 6-yard box
      ctx.strokeRect(px + pw - gbW, py + (ph - gbH) / 2, gbW, gbH)

      // Right penalty spot
      ctx.beginPath()
      ctx.arc(px + pw - pw * 0.115, py + ph / 2, 2, 0, Math.PI * 2)
      ctx.fillStyle = "rgba(255,255,255,0.15)"
      ctx.fill()

      // Right penalty arc
      ctx.beginPath()
      ctx.arc(px + pw - pw * 0.115, py + ph / 2, ph * 0.14, Math.PI * 0.62, Math.PI * 1.38)
      ctx.stroke()

      // Corner arcs
      const cr = pw * 0.018
      ;[[px, py], [px + pw, py], [px, py + ph], [px + pw, py + ph]].forEach(([cx, cy], i) => {
        ctx.beginPath()
        const startAngle = [0, Math.PI / 2, -Math.PI / 2, Math.PI][i]
        ctx.arc(cx, cy, cr, startAngle, startAngle + Math.PI / 2)
        ctx.stroke()
      })

      // Grass stripes (subtle alternating bands)
      const stripeCount = 10
      const stripeW = pw / stripeCount
      for (let i = 0; i < stripeCount; i++) {
        if (i % 2 === 0) {
          ctx.fillStyle = "rgba(255,255,255,0.025)"
          ctx.fillRect(px + i * stripeW, py, stripeW, ph)
        }
      }

      ctx.restore()
    }

    function draw() {
      if (!canvas || !ctx) return
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Base deep gradient
      const baseGrad = ctx.createLinearGradient(0, 0, 0, canvas.height)
      baseGrad.addColorStop(0, "#020509")
      baseGrad.addColorStop(0.5, "#050810")
      baseGrad.addColorStop(1, "#030608")
      ctx.fillStyle = baseGrad
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Draw pitch lines
      drawPitch()

      // Breathing gold glow top
      breatheT += 0.007
      const breathe = 0.07 + Math.sin(breatheT) * 0.025
      const goldGrad = ctx.createRadialGradient(
        canvas.width / 2, 0, 0,
        canvas.width / 2, 0, canvas.width * 0.7,
      )
      goldGrad.addColorStop(0, `rgba(255,215,0,${breathe})`)
      goldGrad.addColorStop(0.4, `rgba(255,180,0,${breathe * 0.25})`)
      goldGrad.addColorStop(1, "rgba(255,215,0,0)")
      ctx.fillStyle = goldGrad
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Subtle side vignette
      const vigLeft = ctx.createLinearGradient(0, 0, canvas.width * 0.25, 0)
      vigLeft.addColorStop(0, "rgba(0,0,0,0.5)")
      vigLeft.addColorStop(1, "rgba(0,0,0,0)")
      ctx.fillStyle = vigLeft
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      const vigRight = ctx.createLinearGradient(canvas.width, 0, canvas.width * 0.75, 0)
      vigRight.addColorStop(0, "rgba(0,0,0,0.5)")
      vigRight.addColorStop(1, "rgba(0,0,0,0)")
      ctx.fillStyle = vigRight
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Particles
      const mouse = mouseRef.current
      const ATTRACT_RADIUS = 180
      const ATTRACT_FORCE  = 0.035

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i]

        // Mouse attraction
        const dx = mouse.x - p.x
        const dy = mouse.y - p.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < ATTRACT_RADIUS && dist > 1) {
          const force = (1 - dist / ATTRACT_RADIUS) * ATTRACT_FORCE
          p.x += dx * force
          p.y += dy * force
        } else {
          // Normal drift
          p.y -= p.speedY
          p.x += p.speedX
        }

        // Brightness boost near cursor
        const nearMouse = dist < ATTRACT_RADIUS
        const maxOpacity = nearMouse ? Math.min(0.9, 0.6 + (1 - dist / ATTRACT_RADIUS) * 0.5) : 0.55

        if (p.y > canvas.height * 0.7) {
          p.opacity = Math.min(p.opacity + p.opacityDelta, maxOpacity)
        } else {
          p.opacity = Math.max(p.opacity - p.opacityDelta * 1.5, 0)
        }

        if (p.opacity > 0) {
          const drawSize = nearMouse ? p.size * (1 + (1 - dist / ATTRACT_RADIUS) * 1.2) : p.size
          // Glow effect for nearby particles
          if (nearMouse && dist < ATTRACT_RADIUS * 0.6) {
            ctx.shadowBlur = 8
            ctx.shadowColor = "rgba(255,215,0,0.8)"
          }
          ctx.beginPath()
          ctx.arc(p.x, p.y, drawSize, 0, Math.PI * 2)
          ctx.fillStyle = p.color + p.opacity + ")"
          ctx.fill()
          ctx.shadowBlur = 0
        }

        if (p.y < -10 || (p.opacity <= 0 && p.y < canvas.height * 0.5)) {
          particles[i] = spawnParticle()
        }
      }

      animId = requestAnimationFrame(draw)
    }

    resize()
    init()
    draw()

    window.addEventListener("resize", resize)
    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener("resize", resize)
      window.removeEventListener("mousemove", onMouseMove)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
    />
  )
}
