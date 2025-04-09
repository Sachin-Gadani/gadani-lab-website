---
title: Contact
nav:
  order: 5
  tooltip: Email, address, and location
---

# {% include icon.html icon="fa-regular fa-envelope" %}Contact

Our lab is hiring for all levels, including lab technician / manager and post-doctoral associate. Interested individuals should send a brief statement of interest, their CV, and contact for 2-3 professional references to gadanis1@pitt.edu

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

{%
  include figure.html
  image="images/photo.jpg"
  caption="Lorem ipsum"
%}

{% endcapture %}

{% capture col2 %}

{%
  include figure.html
  image="images/photo.jpg"
  caption="Lorem ipsum"
%}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 %}

{% include section.html dark=true %}

{% capture col1 %}
The Gadani Lab
University of Pittsburgh
Department of Neurology, PIND
3501 Fifth Avenue 
BST3, 10051 12A
Pittsburgh, PA 15260

{% endcapture %}

{% capture col2 %}

{% endcapture %}

{% capture col3 %}

{% endcapture %}

{% include cols.html col1=col1 col2=col2 col3=col3 %}
