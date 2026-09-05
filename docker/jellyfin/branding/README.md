# Blake Labs Jellyfin Branding

Assets and styling for the private Blake Labs Jellyfin instance.

## Custom CSS

Copy the contents of `custom.css` into:

`Dashboard -> General -> Branding -> Custom CSS code`

The stylesheet intentionally reuses Jellyfin's configured splash image through the `/Branding/Splashscreen` endpoint, so the background can be changed from the Jellyfin admin UI without editing the CSS.

## Login disclaimer

Use this text in the Jellyfin **Login disclaimer** field:

> Coleção privada. Acesso permitido somente a usuários autorizados.

## Visual direction

- Near-black UI
- White typography
- Muted cool gray secondary text
- Acid green (`#b7ff00`) used only as a micro-accent
- Minimal editorial layout
- No third-party theme imports
- Blake Labs wordmark replaces the default Jellyfin visual branding where CSS allows it

Some native Jellyfin clients do not render the same Jellyfin Web CSS, so this customization is primarily intended for web-based clients.
