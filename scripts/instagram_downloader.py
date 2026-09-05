from __future__ import annotations

import getpass
import os
import re
from pathlib import Path

import instaloader


POST_URL_RE = re.compile(r"instagram\.com/(?:p|reel|reels|tv)/([^/?#]+)/?", re.IGNORECASE)


def _loader(output_dir: Path) -> instaloader.Instaloader:
    return instaloader.Instaloader(
        dirname_pattern=str(output_dir / "{target}"),
        filename_pattern="{date_utc:%Y-%m-%d_%H-%M-%S}_{shortcode}",
        download_pictures=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
    )


def _optional_login(loader: instaloader.Instaloader) -> None:
    answer = input("Fazer login no Instagram? [s/N]: ").strip().lower()
    if answer not in {"s", "sim", "y", "yes"}:
        return

    username = input("Usuário do Instagram: ").strip().lstrip("@")
    password = os.getenv("INSTAGRAM_PASSWORD") or getpass.getpass("Senha: ")
    loader.login(username, password)


def _output_dir() -> Path:
    raw = input("Pasta de saída [downloads/instagram]: ").strip()
    path = Path(raw or "downloads/instagram").expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_single_video(loader: instaloader.Instaloader) -> None:
    url = input("Cole a URL do vídeo/Reel: ").strip()
    match = POST_URL_RE.search(url)
    if not match:
        raise ValueError("URL inválida. Use uma URL de post, Reel ou vídeo do Instagram.")

    shortcode = match.group(1)
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    if not post.is_video:
        raise ValueError("O conteúdo informado não é um vídeo.")

    loader.download_post(post, target="single")
    print(f"Vídeo {shortcode} baixado com sucesso.")


def _download_video_posts(loader: instaloader.Instaloader, profile: instaloader.Profile) -> int:
    count = 0
    seen: set[str] = set()

    for post in profile.get_posts():
        if post.is_video and post.shortcode not in seen:
            loader.download_post(post, target=profile.username)
            seen.add(post.shortcode)
            count += 1

    get_reels = getattr(profile, "get_reels", None)
    if callable(get_reels):
        for post in get_reels():
            if post.is_video and post.shortcode not in seen:
                loader.download_post(post, target=profile.username)
                seen.add(post.shortcode)
                count += 1

    return count


def download_account_videos(loader: instaloader.Instaloader) -> None:
    username = input("Conta/perfil para baixar em lote: @").strip().lstrip("@")
    if not username:
        raise ValueError("Informe um usuário do Instagram.")

    profile = instaloader.Profile.from_username(loader.context, username)
    count = _download_video_posts(loader, profile)
    print(f"Concluído: {count} vídeo(s) baixado(s) de @{profile.username}.")


def main() -> None:
    print("\nBlakeLabs Instagram Downloader")
    print("1 - Baixar um vídeo/Reel por URL")
    print("2 - Baixar todos os vídeos de uma conta")

    choice = input("Escolha [1/2]: ").strip()
    output_dir = _output_dir()
    loader = _loader(output_dir)
    _optional_login(loader)

    try:
        if choice == "1":
            download_single_video(loader)
        elif choice == "2":
            download_account_videos(loader)
        else:
            raise ValueError("Opção inválida. Escolha 1 ou 2.")
    except (instaloader.exceptions.InstaloaderException, ValueError) as exc:
        raise SystemExit(f"Erro: {exc}") from exc


if __name__ == "__main__":
    main()
