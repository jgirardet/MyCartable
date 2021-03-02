import PyTest 1.0
import QtQuick 2.15
import "qrc:/js/stringUtils.mjs" as StringUtils

Item {
    id: item

    TestCase {
        function test_diff() {
            let seq_test = [["aa", "aa", -1, -1], ["a", "ab", 1, 2], ["aa", "aabb", 2, 4], ["aaa", "abaa", 1, 2], ["aaa", "abbaa", 1, 3], ["aaa", "bbaaa", 0, 2], ["ac", "ab", 1, 2], ["aacc", "aabb", 2, 4], ["abca", "abda", 2, 3], ["bbbaaa", "cbbaa", 0, 1], ["ccaaa", "bbaaa", 0, 2]];
            // premier sens
            for (let [l, r, s, e] of seq_test) {
                let df = StringUtils.diff(l, r);
                compare(df, [s, e], ` diff('${l}','${r}') == ${df} !=  (${s},${e})`);
            }
            // deuxieme sens
            for (let [l, r, s, e] of seq_test) {
                let df = StringUtils.diff(r, l);
                compare(df, [s, e], ` diff('${r}','${l}') == ${df} !=  (${s},${e})`);
            }
        }

        name: "stringUtils"
    }

}
