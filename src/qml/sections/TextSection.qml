import QtQuick 2.14
import QtQuick.Controls 2.14

/* beautify preserve:start */
TextEdit {
        id: tx
         anchors.centerIn: parent
         /*height: 200
         width: 2*/

         textFormat: TextEdit.RichText
         onTextChanged: {
             print(cursorPosition)


         }
//         onCursorPositionChanged: {
//                if (cursorPosition == length) {
//                    cursorPosition-=1
//                }
//    }
//                h1 {color: red;}
//                p {color: blue;font-size:14pt;}
//blockquote:before,blockquote:after,q:before,q:after { content: ''; content: none;}
//h1 {color:blue; font-size:25; font-weight:800;}
    Component.onCompleted: {
        text = '
        <html><head>
         <style>
html,body,div,span,applet,object,iframe,h1,h2,h3,h4,h5,h6,p,blockquote,pre,a,abbr,acronym,address,big,cite,code,del,dfn,em,img,ins,kbd,q,s,samp,small,strike,strong,sub,sup,tt,var,b,u,i,center,dl,dt,dd,ol,ul,li,fieldset,form,label,legend,table,caption,tbody,tfoot,thead,tr,th,td,article,aside,canvas,details,embed,figure,figcaption,footer,header,hgroup,menu,nav,output,ruby,section,summary,time,mark,audio,video { margin: 0; padding: 0; border: 0; font-size: 100%; font: inherit; vertical-align: baseline;}
article,aside,details,figcaption,figure,footer,header,hgroup,menu,nav,section { display: block;}
body { line-height: 1;}
ol,ul { list-style: none;}
blockquote,q { quotes: none;}
table { border-collapse: collapse; border-spacing: 0;}
body {color: "#363636";background-color: "#E6E6E6";font-family:\'Verdana\'; font-size:20pt; font-weight:400; font-style:normal;}
h1 {
font-family: Verdana;
font-size: 35pt;
color: #FF0000;
font-weight: 600;
text-decoration: underline;
text-transform: uppercase;
}
</style>
        </head><body>
        <p>ligne normale</p>
        <h1>titre</h1>
        <p>du style en fin de <span style="color:purple">lingne</span></p>
        <p>debut de ligne <span style="color:red">rouge</span> suite de ligne</P>
        <p><span style="color:blue;font-size:4pt;">bleu <span style="color:orange">bleu debut </span>debut </span>debut de ligne <span style="color:red">rouge</span> suite de ligne</P>
        </body></html>
        '

    }
    MouseArea {
        anchors.fill: tx
        onPressed:  {

            print(tx.text)
            print(tx.cursorPosition)
            tx.get
        mouse.accepted=false
        }
    }
}
/* beautify preserve:end */