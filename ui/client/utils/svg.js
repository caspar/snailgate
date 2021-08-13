export const visualScale = 150
export const floorSize=0.5

export const width = 800
export const height = 500

export const toSvgX = x => x * visualScale
export const toSvgY = y => height - (y + floorSize) * visualScale
export const fromSvgX = x => x / visualScale
export const fromSvgY = y => (height - y - (floorSize * visualScale)) / visualScale


