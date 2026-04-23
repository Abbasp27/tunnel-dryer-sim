# visuals3d.py
import streamlit.components.v1 as components

def draw_process_simulation(flow_type, length, width, air_speed, material_name, init_m, final_m, t_hot):
    is_counter = "true" if flow_type == "Counter-Current" else "false"
    
    # Convert decimal moisture to percentage for the visual
    start_moist = init_m * 100
    end_moist = final_m * 100
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #0E1117; font-family: 'Segoe UI', sans-serif; overflow: hidden; }}
            canvas {{ background-color: #161821; border-radius: 8px; border: 1px solid #2D303E; }}
        </style>
    </head>
    <body>
        <canvas id="simCanvas" width="950" height="500"></canvas>
        <script>
            const canvas = document.getElementById('simCanvas');
            const ctx = canvas.getContext('2d');
            
            const isCounter = {is_counter};
            const flowSpeed = {air_speed} * 1.8;
            const airSpeed = {air_speed}; 
            const startMoisture = {start_moist};
            const finalMoisture = {end_moist};
            const materialName = "{material_name}";
            const tHot = {t_hot};
            const physicalLength = {length}; 
            
            const tunnelL = Math.max(300, Math.min(700, 250 + (physicalLength * 12))); 
            
            const startX = 220;  
            const tunnelY = 160;
            const beltY = tunnelY + 140;
            
            let particles = [];
            let air = [];

            function drawLabel(text, x, y, color, align, size="11px") {{
                ctx.textAlign = align;
                ctx.fillStyle = color;
                ctx.font = "bold " + size + " 'Segoe UI', sans-serif";
                ctx.fillText(text, x, y);
            }}

            function drawStructure() {{
                drawLabel(materialName + " Drying Process | Target: " + finalMoisture.toFixed(1) + "% | Air Temp: " + tHot + "°C | Air Vel: " + airSpeed.toFixed(1) + " m/s", startX, tunnelY - 90, "#FFFFFF", "left", "15px");

                ctx.fillStyle = 'rgba(35, 37, 51, 0.4)';
                ctx.strokeStyle = '#2D303E';
                ctx.lineWidth = 2;
                ctx.fillRect(startX, tunnelY, tunnelL, 200);
                ctx.strokeRect(startX, tunnelY, tunnelL, 200);

                ctx.fillStyle = '#232533'; ctx.strokeStyle = '#5A607A';
                
                let burnerX = isCounter ? startX + tunnelL - 90 : startX + 10;
                let damperX = isCounter ? startX + 100 : startX + tunnelL - 180;
                let exhaustX = isCounter ? startX + 10 : startX + tunnelL - 90;

                ctx.roundRect(burnerX, tunnelY - 45, 80, 45, 5); ctx.fill(); ctx.stroke();
                drawLabel("GAS BURNER", burnerX + 40, tunnelY - 55, "#FF5A5A", "center");

                ctx.roundRect(startX + 215, tunnelY - 45, 80, 45, 5); ctx.fill(); ctx.stroke();
                drawLabel("BLOWER / MIXER", startX + 255, tunnelY - 55, "#A8B2C3", "center");

                ctx.roundRect(damperX, tunnelY - 35, 70, 35, 5); ctx.fill(); ctx.stroke();
                drawLabel("DAMPER", damperX + 35, tunnelY - 45, "#4CA5FF", "center");

                ctx.roundRect(exhaustX, tunnelY - 45, 80, 45, 5); ctx.fill(); ctx.stroke();
                drawLabel("EXHAUST FAN", exhaustX + 40, tunnelY - 55, "#A8B2C3", "center");

                ctx.strokeStyle = 'rgba(76, 165, 255, 0.6)';
                ctx.setLineDash([5, 3]);
                ctx.beginPath();
                ctx.moveTo(damperX + 35, tunnelY - 35);
                ctx.lineTo(damperX + 35, tunnelY - 70);
                ctx.lineTo(startX + 255, tunnelY - 70);
                ctx.lineTo(startX + 255, tunnelY - 45);
                ctx.stroke();
                ctx.setLineDash([]);
                drawLabel("RETURN DUCT", (damperX + startX + 255)/2, tunnelY - 75, "rgba(76, 165, 255, 0.8)", "center");

                let ductX = isCounter ? startX + tunnelL - 60 : startX + 40;
                ctx.fillStyle = '#1C1E26'; ctx.strokeStyle = '#4CA5FF';
                ctx.fillRect(ductX, tunnelY, 20, 160);
                
                if (isCounter) ctx.fillRect(startX + 250, tunnelY + 160, Math.max(0, tunnelL - 250 + 10), 20);
                else ctx.fillRect(startX + 40, tunnelY + 160, Math.min(260, tunnelL - 40), 20);
                ctx.stroke();

                ctx.strokeStyle = '#8B949E'; ctx.lineWidth = 3;
                ctx.beginPath(); ctx.moveTo(startX - 120, beltY); ctx.lineTo(startX + tunnelL + 100, beltY); ctx.stroke();

                drawLabel("WET FEED IN", startX - 80, beltY - 15, "#4CA5FF", "center");
                drawLabel("DRIED PRODUCT", startX + tunnelL + 50, beltY - 15, "#E2B93B", "center");
                
                drawLabel("Calculated Tunnel Length: " + physicalLength.toFixed(2) + " m", startX + (tunnelL / 2), beltY + 70, "#4CA5FF", "center", "15px");
            }}

            function drawSensorZones() {{
                let points = [];
                let step = physicalLength > 20 ? 4 : 2; 
                for (let d = 0; d <= physicalLength; d += step) {{
                    points.push(d);
                }}
                if (points[points.length - 1] < physicalLength) {{
                    points.push(physicalLength);
                }}

                points.forEach(d => {{
                    let z = d / physicalLength;
                    let m;

                    if (isCounter) {{
                        m = startMoisture - (startMoisture - finalMoisture) * (Math.exp(2.5 * z) - 1) / (Math.exp(2.5) - 1);
                    }} else {{
                        m = finalMoisture + (startMoisture - finalMoisture) * (Math.exp(-2.0 * z) - Math.exp(-2.0)) / (1 - Math.exp(-2.0));
                    }}

                    let px = startX + (z * tunnelL);

                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
                    ctx.setLineDash([4, 4]);
                    ctx.beginPath();
                    ctx.moveTo(px, tunnelY);
                    ctx.lineTo(px, beltY);
                    ctx.stroke();
                    ctx.setLineDash([]);

                    ctx.fillStyle = 'rgba(20, 22, 30, 0.85)';
                    ctx.strokeStyle = 'rgba(76, 165, 255, 0.5)';
                    ctx.lineWidth = 1;
                    ctx.fillRect(px - 25, beltY - 65, 50, 32);
                    ctx.strokeRect(px - 25, beltY - 65, 50, 32);

                    drawLabel("DIST: " + d.toFixed(1) + "m", px, beltY - 52, "#A8B2C3", "center", "9px");
                    drawLabel(m.toFixed(1) + "%", px, beltY - 39, "#4CA5FF", "center", "11px");
                }});
            }}

            // --- UPGRADE 3: Macro Heat-Wave Chevrons ---
            function drawMacroAirflow() {{
                ctx.save();
                ctx.globalAlpha = 0.20; // Semi-transparent
                let spacing = 120;
                
                // Animate the shift based on real-time and flow direction
                let timeOffset = (Date.now() / 25) * (isCounter ? -1 : 1);
                let baseShift = timeOffset % spacing;
                if (baseShift < 0) baseShift += spacing;

                ctx.lineWidth = 18;
                ctx.lineJoin = "round";
                ctx.lineCap = "round";

                // Draw arrows across the tunnel length
                for(let x = startX - spacing + baseShift; x < startX + tunnelL + spacing; x += spacing) {{
                    if (x < startX || x > startX + tunnelL) continue; // Keep inside walls
                    
                    // Color the arrow based on where it is (Hot near burner, cooling down)
                    let zRatio = (x - startX) / tunnelL;
                    let tempRatio = isCounter ? zRatio : (1 - zRatio); 
                    
                    let hue = 10 + (1 - tempRatio) * 40; // Shifts from Red (10) to Gold (50)
                    ctx.strokeStyle = `hsl(${{hue}}, 100%, 50%)`;

                    ctx.beginPath();
                    if (isCounter) {{
                        // Counter-Current: Arrow points LEFT
                        ctx.moveTo(x + 25, tunnelY + 60);
                        ctx.lineTo(x - 15, tunnelY + 100);
                        ctx.lineTo(x + 25, tunnelY + 140);
                    }} else {{
                        // Co-Current: Arrow points RIGHT
                        ctx.moveTo(x - 25, tunnelY + 60);
                        ctx.lineTo(x + 15, tunnelY + 100);
                        ctx.lineTo(x - 25, tunnelY + 140);
                    }}
                    ctx.stroke();
                }}
                ctx.restore();
            }}

            function update() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawStructure();
                drawSensorZones(); 
                drawMacroAirflow(); // Render the giant airflow arrows!

                if (Math.random() > 0.80) particles.push({{ x: startX - 120, y: beltY - 4, m: startMoisture }});
                
                for(let i=particles.length-1; i>=0; i--) {{
                    let p = particles[i]; 
                    p.x += 1.3; 
                    
                    let zRatio = (p.x - startX) / tunnelL;
                    
                    if (zRatio >= 0 && zRatio <= 1) {{
                        if (isCounter) {{
                            p.m = startMoisture - (startMoisture - finalMoisture) * (Math.exp(2.5 * zRatio) - 1) / (Math.exp(2.5) - 1);
                        }} else {{
                            p.m = finalMoisture + (startMoisture - finalMoisture) * (Math.exp(-2.0 * zRatio) - Math.exp(-2.0)) / (1 - Math.exp(-2.0));
                        }}
                    }}
                    
                    if (p.m < finalMoisture) p.m = finalMoisture; 

                    let moistureRatio = (p.m - finalMoisture) / (startMoisture - finalMoisture);
                    if (moistureRatio < 0) moistureRatio = 0;
                    if (moistureRatio > 1) moistureRatio = 1;
                    
                    let dynamicHue = 35 + (moistureRatio * 175); 
                    
                    ctx.fillStyle = "hsl(" + dynamicHue + ", 80%, 55%)";
                    ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, 7); ctx.fill();

                    if(p.x > canvas.width) particles.splice(i, 1);
                }}

                if (Math.random() > 0.45) {{
                    let airStartX = isCounter ? startX + tunnelL - 50 : startX + 50;
                    air.push({{ x: airStartX, y: tunnelY, s: 0 }});
                }}

                // --- UPGRADE 4: Aerodynamic Wind Streaks ---
                for(let i=air.length-1; i>=0; i--) {{
                    let a = air[i];
                    if(a.s === 0) {{ a.y += flowSpeed; if(a.y >= tunnelY + 170) a.s = 1;
                    }} else if(a.s === 1) {{ a.x += isCounter ? -flowSpeed : flowSpeed; if((isCounter ? a.x < startX+450 : a.x > startX+100) && Math.random() < 0.1) a.s = 2;
                    }} else if(a.s === 2) {{ a.y -= flowSpeed * 0.9; if(a.y <= tunnelY + 80) a.s = 3;
                    }} else if(a.s === 3) {{ a.x += isCounter ? -flowSpeed : flowSpeed; let reachedDamper = isCounter ? (a.x <= startX + 135) : (a.x >= startX + 375); if(reachedDamper) {{ if(Math.random() < 0.5) a.s = 5; else a.s = 4; }}
                    }} else if(a.s === 4) {{ a.x += isCounter ? -flowSpeed : flowSpeed; if(a.y > 100) a.y -= flowSpeed;
                    }} else if(a.s === 5) {{ a.y -= flowSpeed; if(a.y <= tunnelY - 70) a.s = 6;
                    }} else if(a.s === 6) {{ a.x += isCounter ? flowSpeed : -flowSpeed; if(isCounter ? a.x >= startX+255 : a.x <= startX+255) a.s = 0; }}

                    // Draw a trailing line instead of a dot
                    ctx.strokeStyle = (a.s >= 5) ? 'rgba(255, 140, 0, 0.6)' : (a.s < 3 ? 'rgba(255, 90, 90, 0.8)' : 'rgba(168, 178, 195, 0.5)');
                    ctx.lineWidth = 4;
                    ctx.lineCap = "round";
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    
                    let tx = a.x, ty = a.y;
                    let tLen = 12; // Length of the wind streak
                    if(a.s===0) ty -= tLen;
                    else if(a.s===1) tx -= (isCounter ? -tLen : tLen);
                    else if(a.s===2) ty += tLen;
                    else if(a.s===3) tx -= (isCounter ? -tLen : tLen);
                    else if(a.s===4) tx -= (isCounter ? -tLen : tLen);
                    else if(a.s===5) ty += tLen;
                    else if(a.s===6) tx -= (isCounter ? tLen : -tLen);
                    
                    ctx.lineTo(tx, ty);
                    ctx.stroke();

                    if(a.y < 0 || a.x < 0 || a.x > 950) air.splice(i, 1);
                }}
                requestAnimationFrame(update);
            }}
            update();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=520)
