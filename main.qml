import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 600
    height: 500
    title: "HelloApp"
    property variant arr: ["a","b"]
    property string com_num: ""
    property color bg_color: "white"
    property color txt_color: "black"
    Text {
        anchors.centerIn: parent
        text: "Hello, World"
        font.pixelSize: 24
    }
    ComboBox {
      id: combo
      editable: true
      model: arr
     onAccepted: {
      if (combo.find(currentText) === -1) {
         model.append({text: editText})
         currentIndex = combo.find(editText)
         com_num = arr[currentIndex]
       }
     }
    }


    Button {
    id: ctrl

    background: Rectangle {
        color: ctrl.pressed ? Qt.darker(bg_color, 1.25) : bg_color
    }

    contentItem: Text {
        text: ctrl.text
        padding: ctrl.padding
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.family: "Segoe UI"
        font.pixelSize: 14
        color: txt_color
    }
}

}