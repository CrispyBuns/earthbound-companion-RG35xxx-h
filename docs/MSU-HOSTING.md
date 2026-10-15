# Soundtrack download sources

The music download is optional. A music-server failure must not prevent Original or Redux game data from being built. Missing PCM tracks use the converted original soundtrack. On Windows 1.0.7, game setup completes with a warning when the optional download cannot finish; retry from **Music & volume → Install / repair soundtrack**.

The downloader retries failed requests and checks alternative sources. The shipped sources are the creator-linked Archive.org download endpoint and two verified Archive storage endpoints. These alternatives help with a failing redirect/download gateway; they share one provider and cannot cover a complete Archive outage. Successfully verified tracks are reused when retrying. Files only receive their final names after size, MD5 and SHA-1 match the pinned 164-track manifest. A cancelled or failed attempt removes its temporary file and preserves the previous final file.

The pack creator also links a [Zeldix mirror](https://www.zeldix.net/t1931-earthbound-msu-1) from the [MaternalBound source](https://github.com/ShadowOne333/MaternalBound-Redux). Its [Box mirror](https://app.box.com/s/fkmjx61w4m7xom1kmir5zk7xv6jx9u8f) is a multipart RAR download, so it is a manual alternative rather than a track-by-track automatic source. Extract its PCM files into the installation's `msu` folder; use Install / repair to verify them. No ROM is needed in the soundtrack folder.

## Adding an independent mirror

The owner can put `msu-sources.json` in the Companion data root (alongside `msu` and `UserData`). Custom sources are tried before the built-in fallbacks:

```json
{
  "sources": ["https://music.example.org/earthbound/v1/"]
}
```

Each source must be an HTTPS folder URL ending in `/`, without credentials, query strings or fragments. It must serve the original filenames directly, such as `eb_msu1-1.pcm`. Editing this source list changes download locations, not the accepted soundtrack bytes. No checksum bypass is provided. Details of failures go to `UserData/msu-setup.log`.

For an owner-operated mirror, coordinate the PCM distribution with ShadowOne333 and the pack's credited contributors. [Cloudflare R2](https://developers.cloudflare.com/r2/pricing/) is one hosting option: its published pricing has no egress bandwidth charge. Use a [custom domain for production public access](https://developers.cloudflare.com/r2/data-access/public-buckets/), retain the versioned path and filenames, and keep the existing fallback URLs. Check the current pricing and account requirements before enabling a service.

Keep soundtrack hosting separate from the game's source/releases. A mirror should contain only the verified PCM tracks and credits; no ROM, game asset pack, saves or private files. New hosting has not been provisioned by this maintenance update.
