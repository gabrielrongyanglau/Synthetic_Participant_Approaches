/* Minimal ZIP writer (stored entries). All file assembly stays in browser memory. */
'use strict';
function makeZip(files){
  const enc=new TextEncoder(),entries=[],parts=[],central=[];let offset=0;
  const crcTable=Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0});
  const crc=b=>{let n=0xffffffff;for(const v of b)n=crcTable[(n^v)&255]^(n>>>8);return (n^0xffffffff)>>>0};
  const header=(size)=>{const a=new Uint8Array(size);return [a,new DataView(a.buffer)]};
  for(let [filename,text] of Object.entries(files)){
    if(/\.csv$/i.test(filename)&&!String(text).startsWith('\ufeff'))text='\ufeff'+text;  // so Excel reads UTF-8
    const name=enc.encode(filename),data=enc.encode(text),checksum=crc(data),[a,v]=header(30+name.length);
    v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x800,true);v.setUint32(14,checksum,true);v.setUint32(18,data.length,true);v.setUint32(22,data.length,true);v.setUint16(26,name.length,true);a.set(name,30);
    parts.push(a,data);entries.push({name,data,checksum,offset});offset+=a.length+data.length;
  }
  let centralSize=0;
  for(const {name,data,checksum,offset:entryOffset} of entries){
    const [a,v]=header(46+name.length);v.setUint32(0,0x02014b50,true);v.setUint16(4,20,true);v.setUint16(6,20,true);v.setUint16(8,0x800,true);v.setUint32(16,checksum,true);v.setUint32(20,data.length,true);v.setUint32(24,data.length,true);v.setUint16(28,name.length,true);v.setUint32(42,entryOffset,true);a.set(name,46);central.push(a);centralSize+=a.length;
  }
  const [end,v]=header(22);v.setUint32(0,0x06054b50,true);v.setUint16(8,entries.length,true);v.setUint16(10,entries.length,true);v.setUint32(12,centralSize,true);v.setUint32(16,offset,true);
  return new Blob([...parts,...central,end],{type:'application/zip'});
}
