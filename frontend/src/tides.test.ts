import { describe, expect, it } from 'vitest'
import type { Extremum } from './types'
import { eventsIn, heightAt, rateAt, sample, snapshot } from './tides'

const H = 60 * 60 * 1000
const base = Date.UTC(2026, 4, 26, 0, 0)

const curve: Extremum[] = [
  { t: base + 1 * H, height: 8, kind: 'H' },
  { t: base + 7 * H, height: 2, kind: 'L' },
  { t: base + 13 * H, height: 7, kind: 'H' },
  { t: base + 19 * H, height: 3, kind: 'L' },
]

describe('tide math', () => {
  it('matches extrema exactly', () => {
    expect(heightAt(curve, curve[0].t)).toBeCloseTo(8, 5)
    expect(heightAt(curve, curve[1].t)).toBeCloseTo(2, 5)
  })

  it('midpoint between H and L is the mean', () => {
    const mid = (curve[0].t + curve[1].t) / 2
    expect(heightAt(curve, mid)).toBeCloseTo(5, 5)
  })

  it('rate sign tracks direction', () => {
    const falling = (curve[0].t + curve[1].t) / 2
    const rising = (curve[1].t + curve[2].t) / 2
    expect(rateAt(curve, falling)).toBeLessThan(0)
    expect(rateAt(curve, rising)).toBeGreaterThan(0)
  })

  it('snapshot reports next events and trend', () => {
    const snap = snapshot(curve, curve[0].t + 2 * H)
    expect(snap.trend).toBe('falling')
    expect(snap.nextLow).toBe(curve[1])
    expect(snap.nextHigh).toBe(curve[2])
  })

  it('sample spans the window inclusively', () => {
    const pts = sample(curve, curve[0].t, curve[3].t, 10)
    expect(pts).toHaveLength(11)
    expect(pts[0].t).toBe(curve[0].t)
    expect(pts[10].t).toBe(curve[3].t)
  })

  it('eventsIn filters to the window', () => {
    const evs = eventsIn(curve, curve[1].t, curve[2].t)
    expect(evs).toHaveLength(2)
  })
})
