class Posts::Approved::Item::Cell < Posts::PostItem::Cell
  option :user_votes, :user
  property :title, :link, :published_at, :description, :id, :category_ids, :votes

  private

  def user_vote
    user_votes.detect { |vote| vote.post_id == id }
  end

  def disabled_button(type)
    "<button type='button' class='button #{button_style(type)}'>#{button_text(type)}</button>"
  end

  def active_button(type)
    link_to nil, class: "button secondary js-#{type}", data: { path: votes_path(type: type, post_id: id) } do
      button_text(type)
    end
  end

  def button_text(type)
    "#{vote_count(type)} <i class=fi-#{type}></i>"
  end

  def vote_count(type)
    positive = (type == "like")
    votes.select { |vote| vote.positive == positive }.count
  end

  def button_style(type)
    if type == "like" && user
      return "success" if user_vote.positive
    elsif user
      return "alert" unless user_vote.positive
    end
    "secondary"
  end
end
