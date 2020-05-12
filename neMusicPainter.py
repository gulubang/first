import matplotlib
import matplotlib.pyplot as plt

def drewler(topWords):

    x=[x[0] for x in topWords]
    y=[x[1] for x in topWords]

    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
    font = matplotlib.font_manager.FontProperties(fname='E:\Program Files\FONTS\ch\萍方简体.ttf')

    plt.figure()
    plt.bar(x,y,facecolor='#9999ff',edgecolor='white')
    plt.xlabel('热词',fontproperties=font)
    plt.ylabel('热词频次',fontproperties=font)
    plt.title('网易云音乐评论热词',fontproperties=font)
    for x,y in zip(x,y):
        plt.text(x,y+0.1,'%d'% y,ha='center',va='bottom')

    plt.show()