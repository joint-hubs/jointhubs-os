"""ThoughtMap entry point: python -m thoughtmap [server|static|run|reset]"""
import sys

if len(sys.argv) > 1 and sys.argv[1] == "server":
    from thoughtmap.web.server import serve
    serve()
elif len(sys.argv) > 1 and sys.argv[1] == "static":
    from thoughtmap.web.server import serve_static
    try:
        serve_static()
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "reset":
    import thoughtmap.config as config
    from thoughtmap.core.embed import get_chroma_client
    print("Resetting ChromaDB collection...")
    client = get_chroma_client()
    try:
        client.delete_collection(config.CHROMA_COLLECTION)
        print(f"  Deleted collection '{config.CHROMA_COLLECTION}'")
    except Exception:
        print(f"  Collection '{config.CHROMA_COLLECTION}' not found, nothing to delete")
    print("Running full pipeline...")
    from thoughtmap.run import main
    main()
else:
    from thoughtmap.run import main
    try:
        main()
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
