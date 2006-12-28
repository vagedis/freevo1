import java.util.Date;

import javax.microedition.lcdui.ChoiceGroup;
import javax.microedition.lcdui.Command;
import javax.microedition.lcdui.CommandListener;
import javax.microedition.lcdui.CustomItem;
import javax.microedition.lcdui.Displayable;
import javax.microedition.lcdui.Font;
import javax.microedition.lcdui.Form;
import javax.microedition.lcdui.Item;
import javax.microedition.lcdui.ItemCommandListener;
import javax.microedition.lcdui.StringItem;

import bemused.BemusedProtocol;

/*
 * Created on May 24, 2004
 *
 * To change the template for this generated file go to
 * Window&gt;Preferences&gt;Java&gt;Code Generation&gt;Code and Comments
 */

/**
 * @author fred
 *
 * To change the template for this generated type comment go to
 * Window&gt;Preferences&gt;Java&gt;Code Generation&gt;Code and Comments
 */
public class MoreActionsForm extends Form implements CommandListener, ItemCommandListener {

	Controller controller;
	Command disconnectCommand;
	Command shutdownCommand;

	Command textCommand;
	Command mainCommand;
	Command numericCommand;
	
	StringItem titleItem;
	StringItem statusItem;
	MoreActionsNavigationWidget naviItem;
	
	/**
	 * @param arg0
	 */
	public MoreActionsForm(Controller controller) {
		super("More actions");
		this.controller = controller;
		
		setCommandListener(this);
		
		naviItem = new MoreActionsNavigationWidget(controller);
		titleItem = new StringItem(null, "---");
		statusItem = new StringItem(null, "Press any key to control");

		//titleItem.setLayout(titleItem.getLayout() | ChoiceGroup.HYPERLINK);
		//titleItem.setLayout(titleItem.getLayout() | 
		//		Item.LAYOUT_CENTER | Item.LAYOUT_NEWLINE_AFTER);
		
		statusItem.setLayout(statusItem.getLayout() | 
				Item.LAYOUT_CENTER | Item.LAYOUT_NEWLINE_AFTER);
		
		//append(titleItem);
		append(naviItem);
		append(statusItem);
		
		mainCommand = new Command("Main", "Main actions", Command.CANCEL, 0);
		addCommand(mainCommand);
		
		numericCommand = new Command("Numeric", "Numeric keys", Command.SCREEN, 2);
		addCommand(numericCommand);

		textCommand = new Command("Text", "Send Text", Command.SCREEN, 2);
		addCommand(textCommand);

	}
	
	public void commandAction(Command cmd, Displayable d) {
		if (cmd == mainCommand) {
			controller.showController();
		}
		else if (cmd == disconnectCommand) {
			controller.disconnect();
		}
		else if (cmd == shutdownCommand) {
			controller.getPlayer().shutdownSystem();
		}
		else if (cmd == mainCommand) {
			controller.showController();
		}
		else if (cmd == textCommand) {
			controller.showTextForm();
		}
		else if (cmd == numericCommand) {
			controller.showNumericForm();
		}
	}

	public void commandAction(Command cmd, Item item) {
	}
}