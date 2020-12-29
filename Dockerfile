FROM pymesh/pymesh

RUN pip install sklearn
RUN pip install trimesh
RUN pip install shapely svglib
RUN pip install transforms3d
RUN pip install triangle

CMD /models/docker-process.sh
