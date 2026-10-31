import {Link} from "react-router-dom";
import {tagLink} from "../utils";

export default function TagChips({tags = []}) {
  if (!tags.length) return null;
  return (
    <div className="tag-chips">
      {tags.map(t => <Link key={t.name} className="tag-chip" to={tagLink(t.name)}>#{t.name}</Link>)}
    </div>
  );
}
