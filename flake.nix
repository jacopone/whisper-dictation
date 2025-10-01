{
  description = "Whisper Dictation - Acqua Voice-like local speech-to-text for NixOS";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python312;
        pythonEnv = python.withPackages (ps: with ps; [
          evdev           # Keyboard event monitoring
          pygobject3      # GTK bindings for UI
          pyaudio         # Audio recording
          numpy           # Audio processing
          scipy           # Signal processing
        ]);

        whisper-dictation = pkgs.stdenv.mkDerivation {
          pname = "whisper-dictation";
          version = "0.1.0";

          src = ./.;

          nativeBuildInputs = [ pkgs.makeWrapper ];

          buildInputs = [
            pythonEnv
            pkgs.whisper-cpp
            pkgs.ffmpeg
            pkgs.ydotool
            pkgs.libnotify
            pkgs.gtk4
            pkgs.gobject-introspection
          ];

          installPhase = ''
            mkdir -p $out/bin
            mkdir -p $out/lib/whisper-dictation

            # Copy Python source
            cp -r src/whisper_dictation $out/lib/whisper-dictation/

            # Create wrapper script
            makeWrapper ${pythonEnv}/bin/python3 $out/bin/whisper-dictation \
              --add-flags "$out/lib/whisper-dictation/whisper_dictation/daemon.py" \
              --prefix PATH : ${pkgs.lib.makeBinPath [
                pkgs.whisper-cpp
                pkgs.ffmpeg
                pkgs.ydotool
                pkgs.libnotify
              ]} \
              --prefix GI_TYPELIB_PATH : "${pkgs.gtk4}/lib/girepository-1.0:${pkgs.gobject-introspection}/lib/girepository-1.0"

            # Copy systemd service
            mkdir -p $out/lib/systemd/user
            cp systemd/whisper-dictation.service $out/lib/systemd/user/
          '';

          meta = with pkgs.lib; {
            description = "Local speech-to-text dictation with push-to-talk for NixOS";
            homepage = "https://github.com/yourusername/whisper-dictation";
            license = licenses.mit;
            platforms = platforms.linux;
          };
        };

      in {
        packages = {
          default = whisper-dictation;
          whisper-dictation = whisper-dictation;
        };

        apps.default = {
          type = "app";
          program = "${whisper-dictation}/bin/whisper-dictation";
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.whisper-cpp
            pkgs.ffmpeg
            pkgs.ydotool
            pkgs.libnotify
            pkgs.gtk4
            pkgs.gobject-introspection

            # Development tools
            python.pkgs.pytest
            python.pkgs.black
            python.pkgs.ruff
          ];

          shellHook = ''
            echo "🎤 Whisper Dictation Development Environment"
            echo "Run: python -m whisper_dictation.daemon"
            export GI_TYPELIB_PATH="${pkgs.gtk4}/lib/girepository-1.0:${pkgs.gobject-introspection}/lib/girepository-1.0"
          '';
        };
      }
    );
}
