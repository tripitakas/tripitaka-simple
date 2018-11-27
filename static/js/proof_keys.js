/* global $ */
(function() {
  'use strict';

  $.extend($.cut, {
    bindMatchingKeys: function() {
      var self = this;
      var on = function(key, func) {
        $.mapKey(key, func, {direction: 'down'});
      };

      // 方向键：在字框间导航
      on('left', function() {
        self.navigate('left');
      });
      on('right', function() {
        self.navigate('right');
      });
      on('up', function() {
        self.navigate('up');
      });
      on('down', function() {
        self.navigate('down');
      });

      var oldChar = [0, '', 0];

      // 响应字框的变化，记下当前字框的关联信息
      self.onBoxChanged(function(info, box) {
        oldChar[0] = box && info.shape.data('order');
        oldChar[1] = box && (info.shape.data('text') || info.shape.data('char')) || '';
        oldChar[2] = info;
        $('#order').val(oldChar[0] || '');
        $('#char').val(oldChar[1]);
      });

      // 改变字框的行内字序号和文字
      $('#change-order').on('submit', function (event) {
        var order = parseInt($('#order').val());
        var char = $('#char').val();
        var info = oldChar[2];

        event.preventDefault();

        if (order && char && info && info.shape) {
          if (order === oldChar[0]) {
            if (oldChar[1] !== char) {    // 只改了字
              self.removeBandNumber(info);
              self.showBandNumber(info, order, char);
              self.unionBandNumbers();
              applyChar(order, char);
            }
          } else {
            // 改变了字序号，就将新序号相应的字框对应到原序号上
            var last = self.findCharByData('order', order);
            var oldText = last && self.removeBandNumber(last);
            if (oldText) {
              last.char_no = oldChar[0] || 0;
              if (last.char_no) {
                applyChar(last.char_no, oldText);
              } else {
                last.line_no = 0;
              }
              self.showBandNumber(last, oldChar[0], oldText);
            }

            // 更新当前字框的关联信息
            self.removeBandNumber(info);
            self.showBandNumber(info, order, char);
            self.unionBandNumbers();
            oldChar[0] = order;
            info.char_no = order;
            info.block_no = $.cut.data.block_no;
            info.line_no = $.cut.data.line_no;
            applyChar(order, char);
          }
          oldChar[1] = char;
        }
      });

      // 将图文匹配校对结果应用到当前行
      function applyChar(order, char) {
        var $block = $('#block-' + $.cut.data.block_no);
        var $line = $block.find('#line-' + $.cut.data.line_no);

        $line.find('span[offset]').each(function(i, el) {
          var $span = $(this);
          var text = $span.text();
          var offset = parseInt($span.attr('offset'));
          if (order > offset && order <= offset + text.length) {
            text = text.split('');
            text[order - offset - 1] = char;
            $span.text(text.join(''));
          }
        });
      }
    }
  });
}());
