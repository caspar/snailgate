// see: http://stackoverflow.com/questions/5204619/how-to-find-the-point-on-an-edge-which-is-the-closest-point-to-another-point
export const findClosetsPointOnEdge = ([x1, y1], [x2, y2], [ a, b ]) => {
  if (y1 === y2)
    return [a, y1]

  if (x1 === x2)
    return [x1, b]

  const m1 = (y2 - y1) / (x2 - x1)
  const m2 = -1/m1

  const x = ( m1*x1 - m2*a - y1 + b ) / ( m1 - m2 )

  const y = m2 * (x - a) + b

  return [x, y]
}

export const getTriangleTop = ([ x1, y1 ], [ x2, y2 ], waterLevel) => {
  const y = y2 - y1
  const x = x2 - x1

  const topX = (waterLevel * x / y) + x1
  const topY = y1 + waterLevel

  return [topX, topY]
}

export const getCentroid = ([x1, y1], [x2, y2]) => {
  return [(x1 + x2) / 2, (y1 + y2) / 2]
}

export const getNormalizedSlope = ([x1, y1], [x2, y2]) => {
  if (x1 === x2) return [0, 1]
  if (y1 === y2) return [1, 0]

  const vector = [x2 - x1, y2 - y1]

  //const normal = [-vector[0], vector[1]]
  const length = getLength([x1, y1], [x2, y2])

  const normalized = [vector[0] / length, vector[1] / length]

  return normalized
}

export const getNormal = ([x1, y1], [x2, y2]) => {
  if (x1 === x2) return [1, 0]
  if (y1 === y2) return [0, 1]

  const vector = [y2 - y1, x2 - x1]

  const normal = [-vector[0], vector[1]]
  const length = getLength([x1, y1], [x2, y2])

  const normalized = [normal[0] / length, normal[1] / length]

  return normalized
}

export const getLength = ([x1, y1], [x2, y2]) => (
  Math.sqrt(Math.pow((y2 - y1), 2) + Math.pow(x2 - x1, 2))
)
