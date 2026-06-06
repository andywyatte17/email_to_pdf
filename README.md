# README

## Description

Take a bunch of emails in a zip (or similar archive) file and turn them into one pdf. Combines tools like python, docker and pandoc.

## Usage

To come...

## Prerequisities

- python3
- docker
- pandoc (within docker)

## Summary - 2026-06-06

- Python tool that reads `.eml` email files from a `.7z` archive and converts them into a single HTML file, intended to be rendered as PDF via pandoc/docker.
- Parses email headers (subject, from, to, date) and body (plain text or HTML), sorting output chronologically.
- Early-stage project — usage docs are a placeholder and the PDF step is not yet implemented.
