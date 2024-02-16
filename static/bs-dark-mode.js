// From: https://web.dev/patterns/theming/theme-switch?hl=de#js
const storageKey = 'theme-preference'
const theme = {}
let toggle;

const onClick = () => {
  setPreference(
    theme.value === 'light'
        ? 'dark'
        : 'light'
    )
}

const getColorPreference = () => {
  value = localStorage.getItem(storageKey)
  if (value)
    return value
  else
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
}

const setPreference = (value) => {
  value = value || getColorPreference()
  theme.value = value
  localStorage.setItem(storageKey, value)
  reflectPreference()
}

const reflectPreference = () => {
  document.firstElementChild
    .setAttribute('data-bs-theme', theme.value)

  toggle?.setAttribute('aria-label', theme.value)
}

// set early so no page flashes / CSS is made aware
setPreference()

window.onload = () => {
  // set on load so screen readers can see latest value on the button
  reflectPreference()

  // now this script can find and listen for clicks on the control
  toggle = document.querySelector('#theme-toggle')
  toggle.addEventListener('click', onClick)
}

// sync with system changes
window
  .matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', ({matches:isDark}) => {
    setPreference(isDark ? 'dark' : 'light')
  })
        