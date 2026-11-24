# Store rules

- Firmware <= 8 MiB.
- Cover exactly 3:4 (e.g. 900x1200, 1152x1536), <= 10 MiB; up to 4 extra 3:4 images.
- Instructions <= 8000 characters per language; changelog <= 4000.
- Chinese instructions required; Chinese changelog required on update.
- validate checks format/size only; open the cover with read_image before submit.
- submit --tag is parsed but not sent; --category only affects print.
