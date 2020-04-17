1. copy and rename config.properties.template to config.properties<br><br>

2. adjust those properties to suit your needs (see comments in the file)<br><br>

3. make sure your environment is correct for Python by running:<br><br>

```bash
pip3 install -r requirements.txt
```

4. write some python code in the 'code' directory<br><br>

```python
import covid_tools as ct
world = ct.fetchWorld()
```
5. or somewhere else loading the serialized world.p file<br><br>
(Note: this file autoupdates in this repo when you pull, but you can also use the dropbox link in README)

```python
import covid_tools as ct
world = ct.fetchWorld('...path/to/world.p')
```
