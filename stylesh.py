stylesh = """QWidget {
  background-color: #192322;
  border: 0px solid #32414B;
  padding: 0px;
  color: #F0F0F0;
  selection-background-color: #1464A0;
  selection-color: #F0F0F0;
}

QWidget:disabled {
  background-color: #192322;
  color: #787878;
  selection-background-color: #14506E;
  selection-color: #787878;
}

QWidget::item:selected {
  background-color: #1464A0;
}

QWidget::item:hover {
  background-color: #148CD2;
  color: #32414B;
}

QLineEdit {
  background-color: #192322;
  padding-top: 2px;
  padding-bottom: 2px;
  padding-left: 4px;
  padding-right: 4px;
  border-style: solid;
  border: 1px solid #32414B;
  border-radius: 4px;
  color: #F0F0F0;
}

QLineEdit:disabled {
  background-color: #192322;
  color: #787878;
}

QLineEdit:hover {
  border: 1px solid #148CD2;
  color: #F0F0F0;
}

QLineEdit:selected {
  background: #1464A0;
  color: #32414B;
}"""