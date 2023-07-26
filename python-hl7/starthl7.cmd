@echo off
:hl7_loop
  python hl7_listener.py
  date /T >> loophl7.log
  time /T >> loophl7.log
  goto :hl7_loop
