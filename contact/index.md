---
title: Contact
nav:
  order: 5
  tooltip: Email, address, and location
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact

{%
  include button.html
  type="email"
  text="gadanis1@pitt.edu"
  link="gadanis1@pitt.edu"
%}
{%
  include button.html
  type="address"
  tooltip="Our location on Google Maps"
  text="3501 Fifth Avenue 
BST3, 10051 12A
Pittsburgh, PA 15260"
  link="https://maps.app.goo.gl/t3SSqcxyWD2Yyo2g9"
%}

{% include section.html %}

{% capture col1 %}

If interested in making a financial gift to our lab's research on Multiple Sclerosis, please email Dr. Gadani at <gadanis1@pitt.edu> or Justin Meyer with the Pitt development office at <jrm233@pitt.edu>. 

{%
  include figure.html
  image="images/labWindow.jpg"
  caption="View of Oakland and the Monongahela river from our lab window."
%}

{% endcapture %}

{% capture col2 %}

{%
  include figure.html
  image="images/Downtown_Pittsburgh_from_Duquesne_Incline_in_the_morning.jpg"
  caption="Downtown Pittsburgh from the Duqesne Incline. (Dllu, Wikimedia)"
%}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}

{% include section.html dark=true %}

{% capture col1 %}
The Gadani Lab\
University of Pittsburgh\
Department of Neurology, PIND\
3501 Fifth Avenue\
BST3, 10051 12A\
Pittsburgh, PA 15260\

{% endcapture %}

{% capture col2 %}

{% endcapture %}

{% capture col3 %}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}
