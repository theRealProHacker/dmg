'use strict'
/*!
 * Adapted from the original Bootstrap's dark mode script: 
    https://getbootstrap.com/docs/5.3/customize/color-modes/#javascript

 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2023 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 */

console.log('Hello from bs-dark-mode.js')

const getStoredTheme = () => localStorage.getItem('theme')
const setStoredTheme = theme => localStorage.setItem('theme', theme)

const getPreferredTheme = () => {
    const storedTheme = getStoredTheme()
    if (storedTheme) {
        return storedTheme
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const setTheme = theme => {
    document.documentElement.setAttribute('data-bs-theme', theme)
}

let currentTheme = getPreferredTheme()
setTheme(currentTheme)

window.onload = () => {
    // const themeSwitcher = document.querySelector('#theme-switcher')
    // themeSwitcher.checked = currentTheme === 'dark'

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (!getStoredTheme()) {
            setTheme(getPreferredTheme())
        }
    })
}