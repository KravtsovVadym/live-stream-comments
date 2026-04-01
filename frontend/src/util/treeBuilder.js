// ---- Converts a flat array of comments into a tree structure
// ---- Each object receives an array of 'replies'.
export const buildTree = (list) => {
  const map = {}
  const tree = []
  // ---- Convert the list into a dictionary object
  // - and add replies as key and list as val
  list.forEach((item) => {
    map[item.id] = { ...item, replies: [] }
  })
  // ---- Distribute the comments: either to the root of the tree,
  // - or to the array of the father's answers
  list.forEach((item) => {
    const node = map[item_id]
    if (item.parent) {
      if (map[item.parent]) {
        map[item.parent].replies.push(nude)
      } else {
        tree.push(node)
      }
    } else {
      tree.push(node)
    }
  })
  return tree
}
