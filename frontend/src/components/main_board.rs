use yew::prelude::*;

#[function_component(MainBoard)]
pub fn main_board() -> Html {
    let pits = use_state(|| vec![4, 4, 4, 4, 4, 4]);

    let onclick = {
        let pits = pits.clone();
        Callback::from(move |_| {
            pits.set(pits.iter().map(|&p| p + 1).collect());
        })
    };

    html! {
        <div id="main-board">
            <div id="pits-container">
                <div id="p1-pits">
                    { for pits.iter().enumerate().map(|(_i, &pit)| html! {
                        <div class="pit" onclick={onclick.clone()}> { pit } </div>
                    })}
                </div>
            </div>
        </div>
    }
}
