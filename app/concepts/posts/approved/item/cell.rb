class Posts::Approved::Item::Cell < Posts::PostItem::Cell
  IMAGE_NAME = { "upvote" => "fi-like", "downvote" => "fi-dislike" }.freeze
  BUTTON_STYLE = { "upvote" => "success", "downvote" => "alert" }.freeze
  UPVOTE = "upvote".freeze
  VOTE_ACCORDION_OPEN = "info_button".freeze

  option :user_votes, :user
  property :title, :link, :published_at, :description, :id, :category_ids, :votes

  private

  def tooltip_wraper(button)
    unless user
      tolltip_title = t("user.should_login")
      tooltip = "<span data-tooltip aria-haspopup='true' data-tooltip='' class='has-tip top' title='#{tolltip_title}'>"
      button = tooltip + button + "</span>"
    end
    button
  end

  def user_vote
    user_votes.detect { |vote| vote.post_id == id }
  end

  def vote_info(type)
    btn_class = user ? VOTE_ACCORDION_OPEN : ""
    button = "<button type='button' class='button #{btn_class} float-left #{BUTTON_STYLE[type]}'
      data-id=#{id}>#{button_text(type)}</button>"
    tooltip_wraper(button)
  end

  def disabled_button(type)
    "<button type='button' class='button #{button_style(type)}'>#{button_text(type)}</button>"
  end

  def active_button(type)
    link_to nil, class: "button #{button_style(type)} js-#{type}",
      data: { type: type, path: votes_path(type: type, post_id: id) } do
      button_text(type)
    end
  end

  def button_text(type)
    "#{vote_count(type)} <i class=#{IMAGE_NAME[type]}></i>"
  end

  def vote_count(type)
    votes.count_by_type(type == UPVOTE)
  end

  def button_style(type)
    if type == UPVOTE && user_vote.present?
      return "success" if user_vote.try(:positive)
    elsif user_vote.present?
      return "alert" unless user_vote.try(:positive)
    end
    "secondary"
  end
end
