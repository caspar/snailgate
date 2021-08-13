import React from 'react'
import { clamp } from 'lodash'
import moment from 'moment'

const clampDurationValue = (val, unit) => {
  switch(unit) {
  case 'minutes':
    return clamp(val, 0, 60) 
  case 'seconds':
    return clamp(val, 0, 60)
  case 'milliseconds':
    return clamp(val, 0, 1000)
  default:
    return val
  }
}

const getUpdatedDuration = (e, existingDuration, unit) => {
  const clampedValue = clampDurationValue(e.target.value, unit)

  const duration = moment(existingDuration)[unit](clampedValue)

  return duration.valueOf()
}

const Clock = ({ disabled, duration, onChange }) => {
  const time = moment(duration)

  return (
    <span>
      <input type='number' value={time.minutes()} onChange={e => onChange(getUpdatedDuration(e, duration, 'minutes'))} disabled={disabled} style={{width: 30}} />
      &nbsp;:&nbsp;
      <input type='number' value={time.seconds()} onChange={e => onChange(getUpdatedDuration(e, duration, 'seconds'))} disabled={disabled} style={{width: 30}} />
      &nbsp;:&nbsp;
      <input type='number' value={time.milliseconds()} onChange={e => onChange(getUpdatedDuration(e, duration, 'milliseconds'))} disabled={disabled} style={{width: 40}} />
    </span>
  )
}

export default Clock
