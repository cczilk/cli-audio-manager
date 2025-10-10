import { useEffect, useRef } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';
import axios from 'axios';

function Terminal() {
  const terminalRef = useRef(null);
  const xtermRef = useRef(null);

  useEffect(() => {
    const term = new XTerm({
      cursorBlink: true,
      theme: {
        background: '#000000',
        foreground: '#4ade80',
        cursor: '#4ade80',
      },
      fontFamily: 'monospace',
      fontSize: 14,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalRef.current);
    fitAddon.fit();

    xtermRef.current = term;

    term.writeln('Terminal Music Player CLI');
    term.writeln('Type "help" for available commands');
    term.write('\r\n$ ');

    let currentLine = '';

    term.onKey(({ key, domEvent }) => {
      const printable = !domEvent.altKey && !domEvent.ctrlKey && !domEvent.metaKey;

      if (domEvent.keyCode === 13) {
        term.write('\r\n');
        handleCommand(currentLine.trim(), term);
        currentLine = '';
        term.write('$ ');
      } else if (domEvent.keyCode === 8) {
        if (currentLine.length > 0) {
          currentLine = currentLine.slice(0, -1);
          term.write('\b \b');
        }
      } else if (printable) {
        currentLine += key;
        term.write(key);
      }
    });

    return () => {
      term.dispose();
    };
  }, []);

  const handleCommand = async (command, term) => {
    const parts = command.split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    try {
      switch (cmd) {
        case 'help':
          term.writeln('Available commands:');
          term.writeln('  play <id>    - Play track');
          term.writeln('  pause        - Pause');
          term.writeln('  stop         - Stop');
          term.writeln('  next         - Next track');
          term.writeln('  prev         - Previous');
          term.writeln('  vol <0-100>  - Set volume');
          term.writeln('  list         - List tracks');
          term.writeln('  now          - Now playing');
          term.writeln('  clear        - Clear');
          break;

        case 'play':
          if (args[0]) {
            await axios.post('http://localhost:5000/api/player/play', { track_id: parseInt(args[0]) });
            term.writeln(`Playing track ${args[0]}`);
          } else {
            term.writeln('Usage: play <id>');
          }
          break;

        case 'pause':
          await axios.post('http://localhost:5000/api/player/pause');
          term.writeln('Paused');
          break;

        case 'stop':
          await axios.post('http://localhost:5000/api/player/stop');
          term.writeln('Stopped');
          break;

        case 'next':
          await axios.post('http://localhost:5000/api/player/next');
          term.writeln('Next track');
          break;

        case 'prev':
          await axios.post('http://localhost:5000/api/player/previous');
          term.writeln('Previous');
          break;

        case 'vol':
          if (args[0]) {
            await axios.post('http://localhost:5000/api/player/volume', { volume: parseInt(args[0]) });
            term.writeln(`Volume: ${args[0]}%`);
          } else {
            term.writeln('Usage: vol <0-100>');
          }
          break;

        case 'list':
          const tracks = await axios.get('http://localhost:5000/api/tracks');
          term.writeln(`ID | Title`);
          tracks.data.forEach(t => term.writeln(`${t.id}  | ${t.title}`));
          break;

        case 'now':
          const status = await axios.get('http://localhost:5000/api/player/status');
          if (status.data.title) {
            term.writeln(`${status.data.title} - ${status.data.artist}`);
          } else {
            term.writeln('Nothing playing');
          }
          break;

        case 'clear':
          term.clear();
          break;

        case '':
          break;

        default:
          term.writeln(`Unknown: ${cmd}`);
      }
    } catch (error) {
      term.writeln(`Error: ${error.message}`);
    }
  };

  return (
    <div className="bg-black border border-green-800 rounded overflow-hidden">
      <div className="bg-gray-900 border-b border-green-800 px-3 py-2 text-green-500 text-sm">
        terminal
      </div>
      <div ref={terminalRef} style={{ height: '400px', padding: '8px' }} />
    </div>
  );
}

export default Terminal;