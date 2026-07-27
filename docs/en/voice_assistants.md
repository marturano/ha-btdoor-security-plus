# Voice assistants

Enable **Quick voice gate** in the integration options to create `switch.apri_cancello_alexa` on the dedicated **Alexa / Google Gate Bridge** virtual device. The switch sends one opening impulse and immediately returns to OFF; it does not show whether the gate is open or closed.

Expose only this switch to Alexa or Google Assistant. Keep `button.apri_cancello`, diagnostic entities and Developer Mode entities private unless you have a deliberate reason to expose them. Configure PIN, confirmation and household restrictions where the assistant supports them.

Alexa discovery and operation have real-user validation. Google Assistant uses the same Home Assistant exposure model but remains unverified on a real account/device until recorded in the compatibility matrix. Never describe an unverified assistant as certified or tested.
