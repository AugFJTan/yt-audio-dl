def set_user_opts(ydl_opts, user_opts):
    if user_opts['metadata']:
        add_metadata(ydl_opts)
    if user_opts['thumbnail']:
        add_thumbnail(ydl_opts)
    if user_opts['sponsorblock']:
        add_sponsorblock(ydl_opts)


def add_metadata(ydl_opts):
    ydl_opts['postprocessors'].extend([
        {
            'key': 'FFmpegMetadata',
            'add_chapters': True,
            'add_infojson': 'if_exists',
            'add_metadata': True
        }
    ])


def add_thumbnail(ydl_opts):
    ydl_opts['outtmpl']['pl_thumbnail'] = ''
    ydl_opts['postprocessors'].extend([
        {
            'key': 'EmbedThumbnail',
            'already_have_thumbnail': False
        }
    ])
    ydl_opts['writethumbnail'] = True


def add_sponsorblock(ydl_opts):
    ydl_opts['postprocessors'].extend([
        {
            'key': 'SponsorBlock',
            'api': 'https://sponsor.ajay.app',
            'categories': {
                'hook',
                'interaction',
                'intro',
                'music_offtopic',
                'outro',
                'preview',
                'selfpromo',
                'sponsor'
            },
            'when': 'after_filter'
        },
        {
            'key': 'ModifyChapters',
            'force_keyframes': False,
            'remove_chapters_patterns': [],
            'remove_ranges': [],
            'remove_sponsor_segments': {
                'hook',
                'interaction',
                'intro',
                'music_offtopic',
                'outro',
                'preview',
                'selfpromo',
                'sponsor'
            },
            'sponsorblock_chapter_title': '[SponsorBlock]: %(category_names)l'
        }
    ])
